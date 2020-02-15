import re
import numpy as np

pitchs = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

chord_notes = {
    '':[0,4,7],
    'm':[0,3,7],
    'dim':[0,3,6],
    'aug':[0,4,8],
}
chord_notes = {
    **chord_notes,
    **{
        '7':chord_notes['']+[10],
        'M7':chord_notes['']+[11],
        'm7':chord_notes['m']+[10],
        'mM7':chord_notes['m']+[11],
        'm7b5':chord_notes['dim']+[10],
        'dim7':chord_notes['dim']+[9],
        'augM7':chord_notes['aug']+[11],
    },
}

scales = {
    '':{
        'root':[0,2,4,5,7,9,11],
        'triad':['','m','m','','','m','dim'],
        'sevens':['M7','m7','m7','M7','7','m7','m7b5'],
    },
    'm':{
        'root':[0,2,3,5,7,8,10],
        'triad':['m','dim','','m','','','dim'],
        'sevens':['m7','m7b5','M7','m7','7','M7','7'],
    },
}

chord_functions = ['T','S','T','S','D','T','D','T']
chord_numbers = ['Ⅰ','Ⅱ','Ⅲ','Ⅳ','Ⅴ','Ⅵ','Ⅶ']

forwards_rule = {
    'T':['T','D','S'],
    'S':['T','D'],
    'D':['T','S'],
}
template_forwards = {
    'kanon':['Ⅰ','Ⅴ','Ⅵ','Ⅲ','Ⅳ','Ⅰ','Ⅳ','Ⅴ'],
    'royal':['Ⅳ','Ⅴ','Ⅲ','Ⅵ'],
    'komuro':['Ⅵ','Ⅳ','Ⅴ','Ⅰ'],
}

key_re = re.compile("^([A-G]#?)(m?)([0-9])$")
note_re = re.compile("^([A-G]#?)([0-9])$")
chord_re = re.compile("^([A-G]#?)([a-zA-Z0-9]*)_([0-9])$")

def note_to_note(note,step):
    m = note_re.match(note)
    i = pitchs.index(m.group(1)) + step
    n = len(pitchs)
    return pitchs[i%n] + str(int(m.group(2)) + i//n)

def note_to_chord(note,symbol):
    m = note_re.match(note)
    return m.group(1) + symbol + '_' + m.group(2)

def chord_to_notes(chord):
    m = chord_re.match(chord)
    return [note_to_note(m.group(1)+m.group(3), step) for step in chord_notes[m.group(2)]]

def scale_chords(key):
    m = key_re.match(key)
    scale = scales[m.group(2)]
    return {
        kind:{
            chord_number:note_to_chord(note_to_note(m.group(1)+m.group(3), scale['root'][i]), scale[kind][i])
            for i,chord_number in enumerate(chord_numbers)
        }
        for kind in ['triad','sevens']
    }

def test():
    chords = scale_chords('A4')['triad']
    print("アスノヨゾラ哨戒班", [(chords[i],chord_to_notes(chords[i])) for i in template_forwards['komuro']])

test()

#TODO イントロABサビ
#TODO 転調
#TODO テンポ
#TODO メロディ
#TODO ベース・ドラム
#TODO 歌詞
