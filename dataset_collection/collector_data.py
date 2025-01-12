import lxml.etree
import json
from bs4 import BeautifulSoup

# question PostTypeId="1" must have AcceptedAnswerId
    # question PostTypeId="2"
    # list_question -> question ID, test question, Tags= &lt;java&gt;
    # list_answer -> find(parent_id=question_id)

# format JSON:
# {"list_string": []}


class DataCollector:
    """ DataCollector Class """

    def __init__(self, file_path="data/raw_data.xml", limit=500, stat_count=5):
        # Init statistic
        self.stats = {}
        self.init_stats(stat_count)

        print("start parsing \n")

        parser = lxml.etree.XMLParser(recover=True)
        root = lxml.etree.parse(file_path, parser)

        self.list_question = root.xpath("row[contains(@Tags, '<java>') and @AcceptedAnswerId]")
        self.list_answer_question = []

        print("get java related xml started \n")

        cnt = 0

        for question in self.list_question:

            if cnt == limit:
                return

            print("start: cnt: %s " % cnt)

            self.list_answer_question.append(question)

            list_answer_from_parent = root.xpath("row[@ParentId=\"" + question.attrib.get("Id") + "\"]")

            ans_cnt = 0
            for answer in list_answer_from_parent:
                self.list_answer_question.append(answer)
                ans_cnt += 1
            if ans_cnt == 0:
                continue
            elif ans_cnt > stat_count:
                if 0 in self.stats:
                    self.stats[0] += 1
                else:
                    self.stats[0] = 1
            else:
                self.stats[ans_cnt] += 1

            cnt += 1

            print("end: cnt: %s" % cnt)

    def init_stats(self, cnt):
        """ Initialise self.stats count """
        for i in range(cnt):
            self.stats[i+1] = 0

        self.stats[0] = 0

    def start_data_collection(self):
        """ start data collection """

        dict_save = {"list_string": []}

        for question in self.list_answer_question:
            dict_save["list_string"].\
                append(self.cleaning_the_java_snippet_code(
                    question.attrib.get("Body")))

        with open('data/data.json', 'w') as outfile:
            json.dump(dict_save, outfile, indent=4)

    def cleaning_the_java_snippet_code(self, str_compare):
        """ code snippet always start with <pre><code> and </pre></code>
        we cannot get the pure BeautifulSoupObject need from string byte
        because BeautifulSoup object does not transform embedded html tag to the actucal ASCII
        """
        change_str = BeautifulSoup(str_compare)
        for tag in change_str.find_all("pre"):
            tag.replaceWith("")

        return change_str.text

if __name__ == "__main__":
    data_collector = DataCollector()
    data_collector.start_data_collection()
