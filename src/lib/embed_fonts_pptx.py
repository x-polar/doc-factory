"""pptx에 TTF 폰트 임베드 (OOXML embeddedFontLst 직접 주입).
PowerPoint 데스크톱(Win/Mac 2019+)이 열 때 임베드 폰트를 사용해
폰트 미설치 머신에서도 동일하게 보인다.
사용: python embed_fonts_pptx.py <in.pptx> <out.pptx> "Font Name=Regular.ttf[,Bold.ttf]" ...
"""
import sys, zipfile, shutil, re, os

def embed(src, dst, fonts):
    """fonts: [(typeface, regular_ttf, bold_ttf_or_None), ...]"""
    shutil.copy(src, dst)
    # zip에 fntdata 추가 + presentation.xml / rels / [Content_Types].xml 수정
    with zipfile.ZipFile(dst, 'a', zipfile.ZIP_DEFLATED) as z:
        names = z.namelist()
        pres = z.read('ppt/presentation.xml').decode('utf-8')
        rels = z.read('ppt/_rels/presentation.xml.rels').decode('utf-8')
        ctypes = z.read('[Content_Types].xml').decode('utf-8')

        # 기존 rId 최대값
        rids = [int(m) for m in re.findall(r'Id="rId(\d+)"', rels)]
        next_rid = max(rids) + 1 if rids else 1

        font_entries = []
        idx = 1
        for typeface, reg, bold in fonts:
            entry = f'<p:embeddedFont><p:font typeface="{typeface}"/>'
            for tag, path in (('regular', reg), ('bold', bold)):
                if not path:
                    continue
                arc = f'ppt/fonts/font{idx}.fntdata'
                z.write(path, arc)
                rid = f'rId{next_rid}'; next_rid += 1
                rels = rels.replace('</Relationships>',
                    f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/font" Target="fonts/font{idx}.fntdata"/></Relationships>')
                entry += f'<p:{tag} r:id="{rid}"/>'
                idx += 1
            entry += '</p:embeddedFont>'
            font_entries.append(entry)

        if 'fntdata' not in ctypes:
            ctypes = ctypes.replace('</Types>',
                '<Default Extension="fntdata" ContentType="application/x-fontdata"/></Types>')

        lst = '<p:embeddedFontLst>' + ''.join(font_entries) + '</p:embeddedFontLst>'
        # embeddedFontLst는 sldMasterIdLst 앞에 위치해야 함
        assert '<p:sldMasterIdLst>' in pres
        pres = pres.replace('<p:sldMasterIdLst>', lst + '<p:sldMasterIdLst>')
        # embedTrueTypeFonts 속성
        pres = pres.replace('<p:presentation ',
                            '<p:presentation embedTrueTypeFonts="1" ', 1)

        # 수정된 파일 재기록 (zipfile은 덮어쓰기 불가 → 새로 조립)
    # 새 zip으로 재조립
    tmp = dst + '.tmp'
    with zipfile.ZipFile(dst, 'r') as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.namelist():
            data = zin.read(item)
            if item == 'ppt/presentation.xml':
                data = pres.encode('utf-8')
            elif item == 'ppt/_rels/presentation.xml.rels':
                data = rels.encode('utf-8')
            elif item == '[Content_Types].xml':
                data = ctypes.encode('utf-8')
            zout.writestr(item, data)
    os.replace(tmp, dst)
    print('embedded', len(fonts), 'fonts →', dst)

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    fonts = []
    for spec in sys.argv[3:]:
        name, files = spec.split('=')
        parts = files.split(',')
        fonts.append((name, parts[0], parts[1] if len(parts) > 1 else None))
    embed(src, dst, fonts)
