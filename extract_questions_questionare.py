from PyPDF2 import PdfReader

class Questionnire:
    def __init__(self):
        pass

    def get_pdf_text(self,pdf):
        text = ""
        file = open(pdf,'rb')
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

    def get_sequence_title(self,text):
        texts_split=text.split("\n")
        texts_split=[text_split.strip() for text_split in texts_split]
        texts_split = [element for element in texts_split if element != ""]
        sequence_title=texts_split[1].split()[0]
        return sequence_title

    def fetch_questions_by_title(self,sequence_title,text):
        questions=text.split(f"({sequence_title}.")
        return questions

    def fetch_questions_from_pdf(self,file_path):
        text=self.get_pdf_text(file_path)
        sequence_title=self.get_sequence_title(text)
        questions=self.fetch_questions_by_title(sequence_title,text)
        questions = questions[1:]

        with open("final_questions.txt", "w", encoding="utf-8") as outfile:
            for question in questions:
                outfile.write(f"{question}\n--------------------------\n")

        return questions
