# ex1.py

import re

ID = r'(?P<ID>[a-zA-Z_][a-zA-Z0-9_]*)'
NUMBER = r'(?P<NUMBER>\d+)'
SPACE = r'(?P<SPACE>\s+)'

patterns = [ID, NUMBER, SPACE]
ignore = ['SPACE']

# Make the master regex pattern
pat = re.compile('|'.join(patterns))


def tokenize(text):
    index = 0
    while index < len(text):
        m = pat.match(text, index)
        if m:
            if m.lastgroup not in ignore:
                yield (m.lastgroup, m.group())
            index = m.end()
        else:
            print('Bad char %r' % text[index])
            index += 1



def test_tokenizer(text):

    for tok in tokenize(text):
        print(tok)

if __name__ == '__main__':

    # Sample usage
    #text01 = 'abc 123 cde 456'
    text02 = 'abc 123 $ cde 456'
    for text in [text02]:
        test_tokenizer(text)