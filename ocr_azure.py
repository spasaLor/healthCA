import os,base64
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models._enums import DocumentAnalysisFeature

from azure.core.credentials import AzureKeyCredential

endpoint ="https://risorsa-per-ocr.cognitiveservices.azure.com/"
key = ""

client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

def esegui_ocr(doc,client):
    text=""
    with open(doc, "rb") as f:
        base64_encoded_pdf = base64.b64encode(f.read()).decode("utf-8")

    analyze_request = {
        "base64Source": base64_encoded_pdf
    }

    poller = client.begin_analyze_document(
        "prebuilt-layout", analyze_request=analyze_request
    )

    result = poller.result()

    for page in result.pages:
       if page.lines:
            for line in page.lines:
                text+=line.content+" "  
    return text


def processa_pdf(folder_path):
    texts = " "
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            doc_path = os.path.join(folder_path, filename)
            text = esegui_ocr(doc_path,client)
            texts+=text+" "
    return texts

if __name__ == "__main__":
    print(processa_pdf("./Reali/1"))

       
