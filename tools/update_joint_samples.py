from pathlib import Path
from html import escape
from urllib.parse import quote
import argparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
START = '<!-- joint-samples:start -->'
END = '<!-- joint-samples:end -->'

def natural_key(path):
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r'(\d+)', path.name)]

def url(path):
    return './' + quote(path.relative_to(ROOT).as_posix())

def audio_files(folder):
    if not folder.is_dir():
        return []
    return sorted((p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in {'.wav', '.mp3', '.ogg', '.m4a'}), key=natural_key)

def visual_cell(folder, stem, label):
    pictures = sorted((p for p in folder.iterdir() if p.is_file() and p.stem.lower() == stem and p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp', '.gif'}), key=natural_key)
    if not pictures:
        return '<div class="joint-image joint-image-missing">Image not available</div>'
    return f'<img class="joint-image" src="{url(pictures[0])}" alt="{escape(label)} for sample {escape(folder.name)}" loading="lazy">'

def audio_cell(clips, number, mode, label, adjustable=False):
    if not clips:
        return '<span class="joint-audio-label">Audio not available</span>'
    player_id = f'joint-audio-{mode}-{number}'
    slider_id = f'joint-clip-{mode}-{number}'
    controls = ''
    default_index = len(clips) - 1 if adjustable else 0
    if adjustable:
        clip_urls = escape(json.dumps([url(clip) for clip in clips]), quote=True)
        controls = f'''
                      <label class="joint-audio-label" for="{slider_id}">Masculinity strength</label>
                      <input type="range" class="slider joint-strength-slider" id="{slider_id}" min="0" max="{len(clips) - 1}" step="1" value="{default_index}" data-clips="{clip_urls}" data-audio-target="{player_id}">
                      <div class="joint-strength-scale"><span>Lowest strength</span><span>Highest strength</span></div>'''
    return controls + f'''
                      <audio id="{player_id}" controls preload="none" src="{url(clips[default_index])}" aria-label="{escape(label)} for sample {number}">
                        Your browser does not support the audio element.
                      </audio>'''

def render():
    rows = []
    for folder in sorted((ROOT / 'joint_cond').iterdir(), key=natural_key):
        if not folder.is_dir():
            continue
        clips = {mode: audio_files(folder / mode) for mode in ('rvtts', 'face', 'full')}
        if not any(clips.values()):
            continue
        if len(clips['rvtts']) > 1:
            raise ValueError(f'Expected a single RVTTS audio file in {folder / "rvtts"}')
        sentence_file = folder / 'sentence.txt'
        sentence = sentence_file.read_text(encoding='utf-8-sig').strip() if sentence_file.is_file() else 'Sentence not available.'
        remarks_file = folder / 'remarks.txt'
        remarks = remarks_file.read_text(encoding='utf-8-sig').strip() if remarks_file.is_file() else ''
        row_span = ' rowspan="2"' if remarks else ''
        number = len(rows) + 1
        rows.append(f'''
                  <tr>
                    <td{row_span} class="joint-artwork-cell">{visual_cell(folder, 'art', 'Full artwork')}</td>
                    <td{row_span} class="joint-face-cell">{visual_cell(folder, 'face', 'Face only')}</td>
                    <td{row_span} class="joint-sentence">{escape(sentence)}</td>
                    <td{row_span}>{audio_cell(clips['rvtts'], number, 'rvtts', 'RVTTS (face only)')}</td>
                    <td>{audio_cell(clips['face'], number, 'face', 'Proposed (face only)', adjustable=True)}</td>
                    <td>{audio_cell(clips['full'], number, 'full', 'Proposed (full artwork)', adjustable=True)}</td>
                  </tr>''')
        if remarks:
            heading, separator, body = remarks.partition('\n')
            formatted_remarks = '<strong>' + escape(heading.strip()) + '</strong>'
            if separator and body.strip():
                formatted_remarks += ': ' + escape(body.strip())
            rows[-1] += (
                '\n                  <tr class="joint-remarks-row">'
                '<td colspan="2"><div class="joint-remarks-field">'
                '<div class="joint-remarks-label">Remarks</div>'
                '<p class="joint-remarks">' + formatted_remarks +
                '</p></div></td></tr>'
            )
    if not rows:
        return '<p class="section-description">No samples available yet.</p>'
    return '''<div class="table-scroll" role="region" aria-label="Joint visual and attribute control samples" tabindex="0">
              <table class="table joint-table">
                <colgroup><col class="joint-artwork-column"><col class="joint-face-column"></colgroup>
                <colgroup><col class="joint-sentence-column"><col span="3" class="joint-output-column"></colgroup>
                <thead>
                  <tr>
                    <th colspan="2" scope="colgroup">Visual input</th>
                    <th rowspan="2" scope="col">Sentence</th>
                    <th rowspan="2" scope="col">RVTTS (face only)</th>
                    <th rowspan="2" scope="col">Proposed (face only)</th>
                    <th rowspan="2" scope="col">Proposed (full artwork)</th>
                  </tr>
                  <tr>
                    <th scope="col">Full artwork</th>
                    <th scope="col">Face only</th>
                  </tr>
                </thead>
                <tbody>''' + ''.join(rows) + '''
                </tbody>
              </table>
            </div>
            <script>
              document.querySelectorAll('.joint-strength-slider').forEach(function (slider) {
                const clips = JSON.parse(slider.dataset.clips);
                slider.addEventListener('input', function () {
                  const player = document.getElementById(this.dataset.audioTarget);
                  player.pause();
                  player.src = clips[Number(this.value)];
                  player.load();
                  player.play().catch(function () {
                    // Keep the player available if automatic playback is blocked.
                  });
                });
              });
            </script>'''

def main():
    parser = argparse.ArgumentParser(description='Rebuild the joint-control table from joint_cond.')
    parser.add_argument('--check', action='store_true', help='Check the table without writing.')
    args = parser.parse_args()
    page = ROOT / 'index.html'
    html = page.read_text(encoding='utf-8')
    if html.count(START) != 1 or html.count(END) != 1:
        raise SystemExit('Expected one joint-samples marker pair in index.html.')
    before, tail = html.split(START, 1)
    _, after = tail.split(END, 1)
    updated = before + START + '\n            ' + render() + '\n            ' + END + after
    if args.check:
        if updated != html:
            raise SystemExit('Table is out of date. Run python tools/update_joint_samples.py')
        print('Joint sample table matches joint_cond.')
    else:
        page.write_text(updated, encoding='utf-8')
        print('Updated joint-control table in index.html.')

if __name__ == '__main__':
    main()
