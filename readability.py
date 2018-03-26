# readability.py
import requests
import re
import sys
import os

class Saver():
    def __init__(self):
        pass

    def save_in_doc(self, lines, url):
        url = self.__name_file__(url)
        index = url.rindex('\\')
        name = url[index+1:]
        url = url[:index+1]
        if not os.path.exists(url):
            os.makedirs(url)
        os.chdir(url)
        print(url)
        f = open(name+'.txt', 'w')
        for line in lines:
            f.write(line)
        f.close()
        return url+name

    def __name_file__(self, url):
        pattern = r'https?:/'
        match = re.search(pattern, url)
        if match:
            url = url[match.end():]
        pattern = r'.s?html'
        match = re.search(pattern, url)
        if match:
            url = url[:match.start()]
        if url[len(url)-1] == '/':
            url = url[:-1]
        repr(url)
        match = True
        while match:
            match = re.search('/', url)
            if match:
                url = url[:match.start()] + '\\' + url[match.end():]
        url = os.getcwd() + url
        return url

class Redact_text():
    def __init__(self):
        pass

    def redact(self, text):
        step = 80
        i = step
        while i < len(text):
            previous = i
            while text[i] != ' ':
                i -= 1
                if i+step <= previous:
                    i = previous
                    break
            text = text[:i+1] + '\n' + text[i+1:]
            i += step
        text += '\n\n'
        return text

    def tab(self, text):
        text = ''.join(list(filter(lambda x: x != '\t', text)))
        return text

    def transfers(self, lines):
        lines = list(filter(lambda x: x != '\n' and x != '', lines))
        return lines

class Text_on_url:
    def __init__(self):
        pass

    def sub(self, text, pattern, repl):
        match = True
        while match:
            match = re.search(pattern, text)
            if match:
                text = text[:match.start()] + repl + text[match.end():]
        return text

    def commas(self, text):
        pattern = r'&[lr]aquo;'
        return self.sub(text, pattern, r'"')

    def space(self, text):
        pattern = r'&nbsp;'
        return self.sub(text, pattern, r' ')

    def copyright(self, text):
        pattern = r'&copy;'
        return self.sub(text, pattern, 'copyright:')

    def dash(self, text):
        pattern = r'&mdash;'
        return self.sub(text, pattern, r'-')

    def href(self, text, url):
        '''
        Применять последним
        '''
        template = r'<a(\s*?\S*?)*?href=\"|\"(\s*?\S*?)*?>|</a>'
        result = ''
        match = re.search(template, text)
        if match:
            line = text[match.end():]
            match2 = re.search(template, line)
            ref = line[:match2.start()]
            line2 = line[match2.end():]
            match3 = re.search(template, line2)
            words = line2[:match3.start()]
            match4 = re.search(r'https?|www|//', ref)
            if not match4:
                match4 = re.search(r'https?://(\s*?\S*?)*?/', url)
                ref = url[:match4.end() - 1] + ref
            result = text[:match.start()] + words + ' [' + ref + ']' + text[match.end() + match2.end() + match3.end():]
        else:
            result = text
        return result

    def img(self, text):
        pattern = r'<img(\s*?\S*?)*?\s(\s*?\S*?)*?>'
        return self.sub(text, pattern, 'image')

    def text_selection(self, text):
        template = r'</?(span|strong)(\s*?\S*?)*?>'
        match = True
        while match:
            match = re.search(template, text)
            if match:
                line = text[match.end():]
                match2 = re.search(template, line)
                words = line[:match2.start()]
                text = text[:match.start()] + words + text[match.end() + match2.end():]
        return text

    def pull_out_text(self, text):
        result = []
        template = r'</?h\d(\s*?\S*?)*?>|</?p(\s*?\S*?)*?>'
        match = True
        while match:
            match = re.search(template, text)
            if match:
                match2 = re.search(template, text[match.end():])
                result.append(text[match.end():match.end() + match2.start()])
                text = text[match.end() + match2.end():]
        return result

    def remove_trash(self, text):
        pattern1 = r'<s(tyle|cript)(\s*?\S*?)*?>'
        pattern2 = r'</s(tyle|cript)(\s*?\S*?)*?>'
        match = True
        while match:
            match = re.search(pattern1, text)
            if match:
                match2 = re.search(pattern2, text[match.end():])
                text = text[:match.start()] + text[match.end() + match2.end():]
        return text

    def special_symbol(self, text):
        text = self.commas(text)
        text = self.space(text)
        text = self.copyright(text)
        text = self.dash(text)
        return text

    def run(self, text, url):
        text = self.remove_trash(text)
        lines = self.pull_out_text(text)
        for i in range(0, len(lines)):
            lines[i] = self.text_selection(lines[i])
            lines[i] = self.img(lines[i])
            lines[i] = self.href(lines[i], url)
            lines[i] = self.special_symbol(lines[i])
        return lines


if __name__ == '__main__':
    url = sys.argv[1]
    r = requests.get(url)
    rb = Text_on_url()
    redact = Redact_text()
    saver = Saver()
    result = rb.run(r.text, url)
    result = redact.transfers(result)
    for i in range(len(result)):
        result[i] = redact.tab(result[i])
        result[i] = redact.redact(result[i])
    file_name = saver.save_in_doc(result, url)

    sys.exit('Successful\nFile location: ' + file_name)
