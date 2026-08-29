import json, sys, os
BASE = os.path.dirname(os.path.abspath(__file__))

def emit(infile, items, segment_notes):
    seg = json.load(open(os.path.join(BASE, 'segments', infile)))
    st = seg['segment_text']
    out_items = []
    for it in items:
        span = it['span_text']
        n = st.count(span)
        if n == 0:
            raise SystemExit('SPAN NOT FOUND: %r' % span[:80])
        start = st.index(span)
        if n > 1:
            print('WARNING: span occurs %d times, using first: %r' % (n, span[:60]))
        end = start + len(span)
        assert st[start:end] == span, 'slice mismatch'
        it['span_char_start'] = start
        it['span_char_end'] = end
        # verify conditions are verbatim substrings of span
        for c in it.get('conditions', []):
            assert c in span, 'condition not in span: %r' % c
        for cs in it.get('conditions_accept_set', []) or []:
            for c in cs:
                assert c in span, 'cond accept not in span: %r' % c
        if it.get('vague_temporal_phrase'):
            assert it['vague_temporal_phrase'] in span, 'vague phrase not in span'
        for p in ('obligor','obligee'):
            v = it.get(p)
            if v and v != 'ABSENT':
                assert v in span, '%s %r not in span' % (p, v)
        for v in it.get('obligor_accept_set', []) or []:
            assert v in span, 'obligor_accept %r not in span' % v
        out_items.append(it)
    rec = {'segment_id': seg['segment_id'], 'doc_id': seg.get('doc_id'),
           'stratum': seg.get('stratum'), 'items': out_items,
           'segment_notes': segment_notes}
    outp = os.path.join(BASE, 'out', infile)
    json.dump(rec, open(outp, 'w'), indent=2, ensure_ascii=False)
    print('WROTE', outp, 'items=', len(out_items))
    for it in out_items:
        print('   [%d:%d] %r' % (it['span_char_start'], it['span_char_end'], it['span_text'][:70]))
