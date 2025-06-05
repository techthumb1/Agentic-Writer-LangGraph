# langgraph_app/agents/publisher.py

import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv
from langchain_core.runnables import RunnableLambda

load_dotenv()

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")

def _send_brevo_email(subject: str, html: str):
    sender = {"name": "Agentic Writer", "email": "no-reply@agentic-writer.ai"}  # Or your verified sender
    to = [{"email": os.getenv("SUBSTACK_EMAIL"), "name": "Substack AutoPost"}]

    email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        sender=sender,
        subject=subject,
        html_content=html
    )

    with sib_api_v3_sdk.ApiClient(configuration) as api_client:
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(api_client)
        try:
            api_instance.send_transac_email(email)
        except ApiException as e:
            raise RuntimeError(f"Brevo API error: {e}")

def _publisher_fn(state: dict) -> dict:
    _send_brevo_email(subject=state["topic"], html=state["formatted_article"])

    export_path = f"generated_content/{state['slug']}.html"
    os.makedirs("generated_content", exist_ok=True)
    with open(export_path, "w") as f:
        f.write(state["formatted_article"])

    return {
        "substack_status": "sent via Brevo",
        "medium_import_path": os.path.abspath(export_path),
        "import_url": "https://medium.com/p/import"
    }

publisher: RunnableLambda = RunnableLambda(_publisher_fn)
