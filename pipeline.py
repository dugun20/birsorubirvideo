"""@birsorubirvideo günlük üretim hattı.

Kullanım:
  python pipeline.py plan                      # sıradaki sorunun planını çıkarır, seslendirme metnini yazdırır
  python pipeline.py build <plan.json> <q.mp3>  # videoyu render eder, kuyruğa ekler
  python pipeline.py status                    # kuyruk durumunu gösterir
"""
import json, os, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, 'state', 'history.json')
OUT = os.path.join(HERE, 'out')


def load():
    with open(STATE, encoding='utf-8') as f:
        return json.load(f)


def save(st):
    tmp = STATE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)


def plan():
    import puzzles
    st = load()
    no = st['last_no'] + 1
    p = puzzles.make(no, {it['key'] for it in st['items']})
    path = os.path.join(OUT, f'soru-{no}.plan.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
    print(json.dumps({'plan': path, 'no': no, 'type': p['type'], 'answer': p['answer'], 'tts': p['tts']}, ensure_ascii=False))


def build(plan_path, q_audio):
    import engine
    with open(plan_path, encoding='utf-8') as f:
        p = json.load(f)
    no = p['no']
    mp4 = os.path.join(OUT, f'soru-{no}.mp4')
    v = engine.Video(p, q_audio)
    v.build(mp4)
    cover_ms = int((v.CD_START - 0.6) * 1000)
    v.frame(cover_ms / 1000).save(os.path.join(OUT, f'soru-{no}.cover.jpg'), quality=90)
    with open(os.path.join(OUT, f'soru-{no}.txt'), 'w', encoding='utf-8') as f:
        f.write(p['caption'])
    st = load()
    st['items'] = [it for it in st['items'] if it['no'] != no]
    st['items'].append(dict(no=no, key=p['key'], type=p['type'], answer=p['answer'], file=f'out/soru-{no}.mp4',
                            caption=p['caption'], cover_ms=cover_ms, created=datetime.date.today().isoformat(), status='kuyrukta'))
    st['last_no'] = max(st['last_no'], no)
    save(st)
    print(json.dumps({'video': mp4, 'no': no, 'cover_ms': cover_ms, 'caption': p['caption']}, ensure_ascii=False))


def status():
    st = load()
    for it in st['items']:
        print(it['no'], it['type'], it['answer'], it['status'], it['file'])


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    {'plan': plan, 'build': lambda: build(sys.argv[2], sys.argv[3]), 'status': status}[cmd]()
