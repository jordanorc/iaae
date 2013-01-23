# -*- coding: utf-8 -*-
from django.utils.encoding import force_unicode
from xml.dom import minidom
from xml.dom.minidom import Document
import re

def aiml_to_question(email):
    from core.models import EMAIL_DATA
    data = email.data.filter(data_type=EMAIL_DATA.AIML)
    questions = []
    
    if data.count() > 0:
        data = data[0]
        
        doc = minidom.parseString(data.data.encode('utf-8'))
        
        aiml = doc.getElementsByTagName("aiml")[0]
    
        for category in aiml.getElementsByTagName("category"):
            pattern = category.getElementsByTagName("pattern")[0].firstChild.nodeValue
            template = category.getElementsByTagName("template")[0].firstChild.nodeValue
            questions.append((force_unicode(pattern), force_unicode(template)))

    return questions

def xml_to_tagged_sentence(email):
    from core.models import EMAIL_DATA
    data = email.data.filter(data_type=EMAIL_DATA.TAGS)
    tagged_sentences = []
    if data.count() > 0:
        data = data[0]
        
        doc = minidom.parseString(data.data.encode('utf-8'))
    
        for sentence in doc.getElementsByTagName("sentence"):
            for word in sentence.getElementsByTagName("word"):
                value = word.getElementsByTagName("value")[0].firstChild.nodeValue
                tag = word.getElementsByTagName("tag")[0].firstChild.nodeValue
                tagged_sentences.append((force_unicode(value), force_unicode(tag)))
    return tagged_sentences

def tagged_sentence_to_xml(tagged_sentence):
    
    # Create the minidom document
    doc = minidom.Document()
    
    # Create the <wml> base element
    sentence = doc.createElement("sentence")
    doc.appendChild(sentence)
    
    for s in tagged_sentence:
        # Create the main <card> element
        word = doc.createElement("word")
    
        world_value = doc.createElement("value")
        world_value.appendChild(doc.createTextNode(s[0]))
        
        world_tag = doc.createElement("tag")
        world_tag.appendChild(doc.createTextNode(s[1]))
    
        word.appendChild(world_value)
        word.appendChild(world_tag)
        
        sentence.appendChild(word)

    # Print our newly created XML
    return doc.toxml()

def questions_to_aiml(questions):
    punctuation = "\"`~!@#$%^&()-_=+[{]}\|;:',<.>/?"
    _puncStripRE = re.compile("[" + re.escape(punctuation) + "]")

    # Create the minidom document
    doc = Document()
    
    # Create the <aiml> base element
    aiml = doc.createElement("aiml")
    doc.appendChild(aiml)
    

    for question, answer in questions:        
        patterns = (re.sub(_puncStripRE, "", question), re.sub(_puncStripRE, "*", question))
        
        for p in patterns:
            category = doc.createElement("category") 
            pattern = doc.createElement("pattern") 
            pattern.appendChild(doc.createTextNode(p.upper()))  
            
            template = doc.createElement("template") 
            template.appendChild(doc.createTextNode(answer))
        
            category.appendChild(pattern)
            category.appendChild(template)
    
            aiml.appendChild(category)

    # Print our newly created XML
    return doc.toxml()
