from google import genai
from google.genai import types

from src.domain.gemini_gateway import IGeminiGateway
from src.domain.receipt_data import ReceiptData
from src.shared.errors import GeminiError, ExtractionError

_PROMPT = """Você é um assistente financeiro que analisa comprovantes.

Analise a imagem do comprovante e extraia: data/hora e valor.

Classifique como:
- "expense": quando o comprovante indica que o usuário PAGOU ou TRANSFERIU dinheiro para outra pessoa/empresa. Exemplos: boletos pagos, PIX enviado, compras no cartão, contas de consumo (luz, água, internet), pagamentos de serviços.
- "income": quando o comprovante indica que o usuário RECEBEU dinheiro. Exemplos: depósito recebido, PIX recebido, pagamento de salário, reembolso, transferência recebida.

Dica: observe palavras-chave como "pagamento", "compra", "débito" (expense) ou "crédito", "depósito", "recebido" (income). Em transferências PIX, verifique se o usuário é o pagador ou o recebedor.

Após extrair os dados, chame a tool send_receipt_data."""

_TOOL_DECLARATION = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="send_receipt_data",
            description="Sends the extracted financial receipt data.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "datetime": types.Schema(
                        type=types.Type.STRING,
                        description="Receipt date and time in YYYY-MM-DDTHH:MM:SS format",
                    ),
                    "amount": types.Schema(
                        type=types.Type.NUMBER,
                        description="Amount in BRL (Brazilian Reais)",
                    ),
                    "type": types.Schema(
                        type=types.Type.STRING,
                        description='Classification: "income" or "expense"',
                        enum=["income", "expense"],
                    ),
                },
                required=["datetime", "amount", "type"],
            ),
        )
    ]
)


class GeminiClient(IGeminiGateway):
    """Gemini gateway implementation: prompt, image+tool, parse tool call."""

    def __init__(self, api_key: str):
        self._client = genai.Client(api_key=api_key)

    async def analyze_receipt(self, image_bytes: bytes, mime_type: str) -> ReceiptData:
        image_part = types.Part.from_bytes(
            data=image_bytes, mime_type=mime_type)

        config = types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=4096,
            tools=[_TOOL_DECLARATION],
        )

        print(f"[gemini_client] Enviando imagem para o modelo gemini-3-flash-preview ({len(image_bytes)} bytes, {mime_type})")
        try:
            response = await self._client.aio.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[image_part, _PROMPT],
                config=config,
            )
            print("[gemini_client] Resposta recebida da LLM com sucesso")
        except Exception as exc:
            print(f"[gemini_client] ERRO na comunicação com Gemini: {exc}")
            raise GeminiError(
                f"Error communicating with Gemini: {exc}") from exc

        return self._parse_tool_call(response)

    @staticmethod
    def _parse_tool_call(response) -> ReceiptData:
        if not response.candidates:
            print("[gemini_client] ERRO: resposta sem candidates")
            raise ExtractionError("Could not extract data from the receipt.")

        candidate = response.candidates[0]
        if not candidate.content or not candidate.content.parts:
            print("[gemini_client] ERRO: resposta sem content/parts")
            raise ExtractionError("Could not extract data from the receipt.")

        for part in candidate.content.parts:
            if part.function_call and part.function_call.name == "send_receipt_data":
                args = part.function_call.args
                print(f"[gemini_client] Tool call parsed — send_receipt_data(datetime={args['datetime']}, amount={args['amount']}, type={args['type']})")
                return ReceiptData(
                    datetime=args["datetime"],
                    amount=float(args["amount"]),
                    type=args["type"],
                )

        print("[gemini_client] ERRO: nenhuma tool call 'send_receipt_data' encontrada na resposta")
        raise ExtractionError("Could not extract data from the receipt.")


# Esse arquivo possui código gerado com IA
