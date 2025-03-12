from huggingface_hub import InferenceClient
import gradio as gr

client = InferenceClient(api_key="")

def ritorna_docs():
    docs={
        'Documento 1':{
            "Città": "Catania",
            "Ospedale": "Azienda Ospedaliera Universitaria Policlinico - Vittorio Emanuele",
            "Data di ricovero": "02/01/2021",
            "Data di dimissione": "07/01/2021",
            "Diagnosi": "Metrorragia resistente a terapia medica",
            "Sintomi": "Anemia, Metrorragia proveniente dai genitali esterni",
            "Riassunto": "La paziente è stata ricoverata nella Azienda Ospedaliera Universitaria Policlinico - Vittorio Emanuele per un periodo di ricovero ordinario dal 02/01/2021 al 07/01/2021. Ha subito intervento ginecologico il 05/01/2021 e la diagnosi di ingresso era Metrorragia resistente a terapia medica. Si è dimessa regolarmente il 07/01/2021.",
            "Link":"https://link_1"
        },

        'Documento 2':{
            "Città": "Catania",
            "Ospedale": "Azienda Ospedalieri - Universitaria 'Policlinico - Vittorio Emanuele'",
            "Data di ricovero": "07/01/2021",
            "Data di dimissione": "13/01/2021",
            "Diagnosi": "Dissezione aorta toraco-addominale tipo B",
            "Sintomi": "Dolo toracico migrante e persistente",
            "Riassunto": "Il paziente, è un residente di Catania, di età 59 anni. È stato ricoverato all'Azienda Ospedalieri - Universitaria 'Policlinico - Vittorio Emanuele' di Catania, in un reparto di chirurgia vascolare dal 7 gennaio al 13 gennaio 2021. Il paziente ha subito una procedura di posizionamento di endoprotesi aortica dalla origine dell'aorta succlavia di sinistra fino a circa 4 cm dall'origine del triparto celiaco durante il suo ricovero. La diagnosi finale è stata una dissezione aorta toraco-addominale tipo B. Al paziente è stato consigliato di sottoporlo alla terapia di dimissione. La terapia domiciliare non è stata modificata e richiede il controllo dell'emocromo completo e prove emocoagulative a 15-30-45 giorni dalla dimissione. Il successivo iter diagnostico-terapeutico prevede un follow-up chirurgico. Il controllo post-operatorio è previsto il 24/01/2021 alle ore 11:30 presso l'Ambulatorio sito al piani-2 del Pad. 1. Si prega di presentarsi con la lettera di dimissione.",
            "Link":"https://link_2"
        },

        'Documento 3':{
            "Città": "Catania",
            "Ospedale": "Policlinico - Vittorio Emanuele",
            "Data di ricovero": "20/01/2021",
            "Data di dimissione": "Data non specificata",
            "Diagnosi": "Sclerosi Multipla",
            "Sintomi": "Formicolio e deficit di forza agli arti inferiori, in particolare il sinistro",
            "Riassunto": "Il paziente è ricoverato all'ospedale Policlinico - Vittorio Emanuele di Catania per la sua diagnosi di Sclerosi Multipla. Ha avuto precedenti ricoveri e visite ambulatoriali presso lo stesso ospedale. La sua terapia attuale è la Gilenya e si raccomanda la massima aderenza alla stessa. Nuovi esami ematici, RMN del cervello e tronco encefalico, colonna cervicale e toracica senza e con contrasto ogni anno, visita dermatologica, cardiologica e oculistica alle frequenze specificate sono richiesti.",
            "Link":"https://link_3"
        },

        'Documento 4':{
            "Città": "Catania",
            "Ospedale": "Policlinico 'G. Rodolico - San Marco'",
            "Data di ricovero": "11/11/2021",
            "Data di dimissione": "23/12/2021",
            "Diagnosi": ["Carcinoma del polmone", "Adenocarcinoma del polmone sinistro localmente avanzato"],
            "Sintomi": ["Dolenzia sternale al manubrio da esiti chirurgici", "Scarsa tosse", "Non emottisi", "Non febbre", "Calo ponderale di 5 kg negli ultimi 2 mesi", "Dolenzia lombare e al fianco destro irradiata fino in sede inguinoscrotale"],
            "Riassunto": "Il paziente è stato ricoverato per una valutazione di un adenocarcinoma del polmone localmente avanzato. Durante il ricovero è stato visitato dalla Oncologia Day Service e successivamente da Chirurgia Toracica. Il paziente presenta anche dolenze sulla colonna vertebrale e dolori irradiati fino in sede inguinoscrotale. L'esame di tromba coronarica ha evidenziato un le Molti noduli satelliti di diverse dimensioni sono presenti in diverse zone della sua anatomia torace, tra cui l'apicale del lobo inferiore sinistro polmonare, la loggia di Barety, l'arco aortico, paramediastinica laterale destra. Il paziente è stato sottoposto a una biopsia bronchiale, la quale ha evidenziato l'adenocarcinoma moderatamente differenziato, TTF1+, CK7+, p40-, cromogranina-, CD56-, sinaptofisina -... PD-L1: positivo (TPS 1-49%). Una PET ha eleventato accumuli linfonodali in diverse zone del suo corpo.",
            "Link":"https://link_4"
        }
    }
    return docs

def chatbot(input_text, history=[]):
    reports=ritorna_docs()
    messages = [{"role": "system", "content": f"""Sei un assistente medico potenziato con IA. Il tuo compito è aiutare gli utenti a trovare referti medici specifici ponendo domande pertinenti. In base alle loro risposte, restringi la selezione dei referti e convalida quello corretto.
                - Utilizza un linguaggio italiano semplice e chiaro per guidare gli utenti attraverso il processo.
                - Conferma sempre i dettagli forniti dall'utente.
                - Per trovare il referto corretto chiedi all'utente l'ospedale che lo ha prodotto, una data anche approssimativa del referto e il motivo del ricovero.
                - In caso di dubbi, fai domande di chiarimento per perfezionare la ricerca.
                - Rispondi in modo cortese ed empatico, assicurandoti che l'utente si senta supportato.
                - Quando ritieni di aver trovato il referto corretto dai il link all'utente.
                 ** Questo è l'indice dei referti che hai a disposizione, non condividerlo con l'utente **: {reports}. 
                 """}]
    
    for user_input, bot_response in history:
        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "assistant", "content": bot_response})
    
    messages.append({"role": "user", "content": input_text})

    try:
        completion = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=messages,
            max_tokens=300,
        )
        bot_response = completion.choices[0].message.content
    except Exception as e:
        bot_response = f"Error: {str(e)}"
    
    history.append((input_text, bot_response))
    
    return history, history,""

with gr.Blocks() as demo:
    gr.Markdown("# Recupero referti medici")
    chatbot_box = gr.Chatbot(label="Assistente IA",value=[[None, "Come posso aiutarti?"]])
    user_input = gr.Textbox(placeholder="Inserisci qui il testo...", container=False,scale=7)
    submit_button=gr.Button("Invia")
    clear_button = gr.Button("Cancella conversazione")
    history_state = gr.State([])

    def clear_history():
        return [], [],""

    user_input.submit(chatbot, [user_input, history_state], [chatbot_box, history_state, user_input])
    clear_button.click(clear_history, [], [chatbot_box, history_state])
    submit_button.click(chatbot, [user_input, history_state], [chatbot_box, history_state])
    demo.title="Recupero referti medici"

if __name__ == "__main__":
    demo.launch()
