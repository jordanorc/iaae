from mail.models import EmailData, EMAIL_DATA
import aiml
import os
import tempfile

def check_answer(question):
    kernel = aiml.Kernel()
    
    # busca todos os dados de arquivos aiml
    data_files = EmailData.objects.filter(data_type=EMAIL_DATA.AIML)
    
    for data in data_files:
        (temp_filedescriptor, temp_filepath) = tempfile.mkstemp()
        data_file = open(temp_filepath, "w+b")

        data_file.write(data.data.encode('utf-8'))
        data_file.close()
        
        kernel.learn(temp_filepath)
        
        os.remove(temp_filepath)
    
    answer = kernel.respond(question)
    if not answer:
        answer = False
    return answer
        
        
        