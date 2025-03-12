from azure.ai.textanalytics import TextAnalyticsClient,AnalyzeHealthcareEntitiesAction,AbstractiveSummaryAction,RecognizeEntitiesAction
from azure.core.credentials import AzureKeyCredential
from dateutil.parser import parse
from datetime import date
import re,json
from dateutil.parser._parser import ParserError

key=""
endpoint="https://risorsa-ner.cognitiveservices.azure.com/"

ta_credential = AzureKeyCredential(key)
ta_client = TextAnalyticsClient(endpoint=endpoint, credential=ta_credential)

def controllo_date(data):
    match = re.match(r'(\d{2})/(\d{2})/(\d{4,})', data)
    
    #correzione per date in cui l'anno ha più di 4 cifre
    if match:
        day, month, year = match.groups()
        if len(year) > 4:
            year = year[:4]

        data = f"{day}/{month}/{year}"
    
    try:
        parsed_date = parse(data, dayfirst=True, fuzzy=False)
        if parsed_date.year == 2024:
            raise ParserError
        return parsed_date.strftime('%d/%m/%Y')
    except (ParserError, ValueError):
        return None
    
def controllo_citta(citta):
    with open('./comuni.json','r',encoding='utf-8') as file:
        comuni=json.load(file)
        for entry in comuni:
            if citta == entry["nome"]:
                return True
        return False 
    
unita_operative=[
                "anatomia patologica",
                "anestesia e rianimazione",
                "cardiochirurgia",
                "cardiologia",
                "chirurgia generale",
                "chirurgia pediatrica",
                "chirurgia toracica",
                "chirurgia vascolare",
                "clinica chirurgica",
                "clinica neurologica",
                "clinica oculistica",
                "clinica odontoiatrica",
                "clinica ortopedica",
                "clinica pediatrica",
                "clinica psichiatrica",
                "clinica urologica",
                "degenza",
                "dermatologia",
                "ematologia",
                "ematologia ed oncologica pediatrica",
                "uoc farmacia",
                "gastroenterologia",
                "igiene ospedaliera",
                "laboratorio analisi",
                "malattie endocrine, del ricambio e della nutrizione",
                "medicina del lavoro",
                "medicina e chirurgia d'accettazione e d'urgenza",
                "medicina interna",
                "medicina legale",
                "medicina trasfusionale",
                "neuropsichiatria infantile",
                "oncologia",
                "ostetricia e ginecologia",
                "otorinolaringoiatria",
                "pneumologia",
                "pronto soccorso",
                "ps",
                "radioterapia oncologica",
                "anestesia e rianimazione",
                "angiologia",
                "broncopneumologia pediatrica",
                "cardiologia pediatrica (servizio)",
                "cardiologia utic",
                "chirurgia generale",
                "chirurgia maxillo facciale",
                "chirurgia toracica",
                "chirurgia vascolare",
                "farmacia",
                "fisica sanitaria",
                "malattie infettive e tropicali",
                "medicina generale",
                "medicina nucleare",
                "nefrologia e dialisi",
                "neurochirurgia",
                "neurologia",
                "ortopedia",
                "ostetricia e ginecologia e ps",
                "patologia ostetrica",
                "pediatria",
                "psicologia",
                "radiologia",
                "radiologia muscolo scheletrica",
                "recupero e riabilitazione funzionale",
                "reumatologia",
                "dietologia e malattie della nutrizione",
                "psichiatria",
                "terapia del dolore",
                "urologia",
                "utin e neonatologia"
]

sintomi_scartare=["dolente","dolenti","nascita","mobile",'scarsa compliance', 'inefficacia clinica', 'sente più soddisfatto', 'stabilità clinica',"malattia",'Incremento volumetrico', 'Disomogenea', 'Disomogeneamente aumentata di dimensioni','iter', 'segni clinici','Emocromo']

def esegui_ner_summary(testo_ocr):
    analysis_results = {
        "Città":[],
        "Valutazione Triage":"",
        "Ospedale":"",
        "Data di Ricovero": [],
        "Data di Dimissioni": [],
        "Diagnosi": [],
        "Sintomi":[],
        "Reparti Visitati":[],
        "Riepilogo":""
    }

    text = [testo_ocr]
    regex = r"(?:UNITÀ OPERATIVA:|Unità Operativa:)\s+((\w+\s*){1,3})"
    match = re.search(regex, testo_ocr)
    if match:
        analysis_results["Reparti Visitati"].append(match.group(1).strip().capitalize())

    poller = ta_client.begin_analyze_actions(
        text,
        display_name="Text Analysis",
        actions=[RecognizeEntitiesAction(),
            AnalyzeHealthcareEntitiesAction(),
            AbstractiveSummaryAction(sentence_count=6)
        ],
        language='it',
    )
    document_results = poller.result()
    for action_results in document_results:
        for result in action_results:
            if result.kind == "AbstractiveSummarization":
                for summary in result.summaries:
                    analysis_results["Riepilogo"] = summary.text
            
            #individua Città e ospedale del referto
            elif result.kind == "EntityRecognition":
                for entity in result.entities:
                    if entity.category=='Location' and entity.subcategory=='City':
                        citta= entity.text.capitalize()
                        if controllo_citta(citta) and citta not in analysis_results["Città"]:
                            analysis_results["Città"].append(citta)
                    elif entity.category == 'Organization' and 'Policlinico' in entity.text:
                        analysis_results["Ospedale"]=entity.text

            elif result.kind == 'Healthcare':
                for entity in result.entities:
                    #individua i reparti citati nella cartella
                    if entity.category=='CareEnvironment':
                        if entity.text.lower() in unita_operative and entity.text.capitalize():# not in analysis_results['Reparti Visitati']:
                            analysis_results['Reparti Visitati'].append(entity.text.capitalize())
                    
                    #individua i sintomi riportati
                    if entity.category == 'SymptomOrSign' and entity.text.capitalize() not in analysis_results['Sintomi'] and entity.text.lower() not in sintomi_scartare:
                        analysis_results['Sintomi'].append(entity.text.capitalize())

                for relation in result.entity_relations:
                    relation_type = relation.relation_type
                    roles = {role.name: role.entity.text for role in relation.roles}
                
                #individua date di ricovero e dimissioni
                    if relation_type == "TimeOfEvent":
                        event_text = ""
                        event_time = ""
                        
                        for role in relation['roles']:
                            if role.name == 'Event':
                                event_text = role['entity']['text'].lower()
                            if role.name == 'Time':
                                formatted_date = controllo_date(role['entity']['text'])
                                today=date.today()
                                if formatted_date == today:
                                    pass
                                elif formatted_date is not None:
                                    event_time = formatted_date
                        
                        if event_text.lower() in ['ingresso', 'ammissione','ricovero'] and event_time not in analysis_results["Data di Ricovero"] and event_time not in analysis_results["Data di Dimissioni"]:
                            analysis_results["Data di Ricovero"].append(event_time)
                        elif event_text.lower() in ['dimissione', 'dimesso'] and event_time not in analysis_results["Data di Dimissioni"] and event_time not in analysis_results["Data di Ricovero"]:
                            analysis_results["Data di Dimissioni"].append(event_time)
                  
                  #individua sintomi  
                    if relation_type == "TimeOfCondition":
                        condition = roles.get('Condition')
                        if condition and condition.capitalize() not in analysis_results["Sintomi"] and condition.lower() not in sintomi_scartare:
                            analysis_results["Sintomi"].append(condition.capitalize())
                    
            elif result.is_error:
                print(f"...Errore: '{result.error.message}' codice errore: '{result.error.code}'")

    # individua le diagnosi
    pattern_ingresso = r'Diagnosi di ingresso\s+([A-Z.\s]+)'
    pattern_dimissione = r'Diagnosi di dimissione\s+([A-Z.\s]+)'

    diagnosi_ingresso = re.search(pattern_ingresso, testo_ocr)
    diagnosi_dimissione = re.search(pattern_dimissione, testo_ocr)

    if diagnosi_ingresso:
        analysis_results['Diagnosi'].append(diagnosi_ingresso.group(1).capitalize().strip()[:-1])
    else:
        None

    if diagnosi_dimissione:
        dia = diagnosi_dimissione.group(1).capitalize().strip()[:-1]
        if dia not in analysis_results['Diagnosi']:
            analysis_results['Diagnosi'].append(dia)
    else:
        None

    #individua la valutazione del triage (Codice bianco, verde ...)
    pattern = r'(Appropriatezza|Priorità):\s*(\w+)'

    match = re.search(pattern, testo_ocr, re.IGNORECASE)
    if match:
        codice_triage = match.group(2)
        match codice_triage:
            case 'B':
                analysis_results['Valutazione Triage']='Codice Bianco'
            case 'V':
                analysis_results['Valutazione Triage']='Codice Verde'
            case 'A':
                analysis_results['Valutazione Triage']='Codice Arancione'
            case 'R':
                analysis_results['Valutazione Triage']='Codice Rosso'
            case _: 
                analysis_results['Valutazione Triage']='Codice '+codice_triage
    else:
        None

    return analysis_results

