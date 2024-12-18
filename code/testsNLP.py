import spacy

#nlp = spacy.load("en_core_web_trf")
nlp = spacy.load("es_core_news_sm")

doc = nlp("Apple is looking at buying U.K. startup for $1 billion")
doc = nlp("Estamos buscando empresas de seguimiento como Quectel")

for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)
    
for token in doc:
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
            token.shape_, token.is_alpha, token.is_stop)
