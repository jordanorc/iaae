# -*- coding: utf-8 -*-
from mail.models import EMAIL_DATA
from xml.dom import minidom
from xml.dom.minidom import Document

def xml_to_tagged_sentence(email):
    data = email.data.filter(data_type=EMAIL_DATA.TAGS)
    if data.count>0:
        data = data[0]
    doc = minidom.parseString(data.data)
    
    tagged_sentences = []
    for sentence in doc.getElementsByTagName("sentence"):
        for word in sentence.getElementsByTagName("word"):
            value = word.getElementsByTagName("value")[0].firstChild.nodeValue
            tag = word.getElementsByTagName("tag")[0].firstChild.nodeValue
            tagged_sentences.append((value, tag))
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
    
    # Create the minidom document
    doc = Document()
    
    # Create the <aiml> base element
    aiml = doc.createElement("aiml")
    doc.appendChild(aiml)
    
    category = doc.createElement("category") 
    
    for question, answer in questions:
        pattern = doc.createElement("pattern") 
        pattern.appendChild(doc.createTextNode(question))
        
        template = doc.createElement("template") 
        template.appendChild(doc.createTextNode(answer))
    
        category.appendChild(pattern)
        category.appendChild(template)
    
        aiml.appendChild(category)

    # Print our newly created XML
    return doc.toxml()
