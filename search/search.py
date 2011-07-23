#!/usr/bin/env python
import Levenshtein as l

def fuzzy_match(searchPhrase, sentence):
    """
    Perform fuzzy search for searchPhrase in sentence.
    Returns a tuple: number of matched words, ratio, list of searchKeys found
    """
    searchKeys = searchPhrase.split()
    match = 0
    keysFound = []
    for searchKey in searchKeys:
        if (sentence.find(searchKey) != -1):
            match = match + 1
            keysFound.append(searchKey)

    totalWords = len(sentence.split())
    """
    try:
        ratio = match/float(totalWords)
        if (ratio < 0):
            ratio = 0.0
    except:
        ratio = 0.0
    """
    ratio = l.ratio(searchPhrase, sentence)

    return (match, (ratio, keysFound))

def search(searchPhrase, lines):
    """
    This method takes as arguments:
    1. searchPhrase (type:string) which is the expression to be searched for
    2. lines (type: list of strings) where every item of lines will be searched for searchPhrase

    Returns a dictionary
    """
    formatted_lines = []
    d = {}
    for line in lines:
        formatted_sentence = line
        if line.find(searchPhrase) == -1:
            match, (ratio, keysFound) = fuzzy_match(searchPhrase, line)
            if match > 0:
                for key in keysFound:
                    formatted_sentence = formatted_sentence.replace(key, "<b>"+key+"</b>", 1)
                if d.has_key(match):
                    d[match].append((ratio, formatted_sentence))
                else:
                    d[match] = [(ratio, formatted_sentence)]
        else:
            #ratio = len(searchPhrase)/float(len(line))
            ratio = l.ratio(searchPhrase, line)
            formatted_sentence = formatted_sentence.replace(searchPhrase, "<b>"+searchPhrase+"</b>",1)
            if d.has_key('contains'):
                d['contains'].append((ratio, formatted_sentence))
            else:
                d['contains'] = [(ratio, formatted_sentence)]
    return d

if __name__ == '__main__':
    """This is an example on how to use the search method"""
    lines = [
    'a b c d e f',
    'b c d e a g',
    'e f a b c h',
    'g h a f c d',
    'm n o p q r',
    'a b c',
    'b a d',
    'c f g',
    ]
    searchPhrase = 'a b c'
    d = search(searchPhrase, lines)
    keys = d.keys()
    if d.has_key('contains'):
        print "-"*70
        print "CONTAINS"
        print "-"*70
        entries = d['contains']
        entries.sort()
        entries.reverse()
        for entry in entries:
            print entry[1]
	keys.remove('contains')
    keys.sort()
    keys.reverse()
    for key in keys:
        print '-'*70
        print '%d matches' %key
        print '-'*70
        entries = d[key]
        entries.sort()
        entries.reverse()
        for entry in entries:
            print entry[1]
    if d == {}:
      print 'Search Phrase Not Found'

