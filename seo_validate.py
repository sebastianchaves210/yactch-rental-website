#!/usr/bin/env python3
"""SEO Validation Script — validates output/ HTML files against seo-reference.json"""

import json
import os
import re
from html.parser import HTMLParser
import html

BASE = "/Users/sebastianchaves/Desktop/Yacht Rental Design"
OUTPUT = os.path.join(BASE, "output")
SEO_REF = os.path.join(BASE, "seo-reference.json")


def decode_entities(text):
    """Decode HTML entities and normalize whitespace."""
    if text is None:
        return ""
    text = html.unescape(text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


class HTMLExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta_desc = ""
        self.canonical = ""
        self.h1s = []
        self.h2s = []
        self.h3s = []
        self.images = []  # list of {src, alt}
        self.links = []   # all href values from <a> and <link>
        self.has_data_modal = False
        self._current_tag = None
        self._current_text = ""
        self._in_heading = None  # 'h1', 'h2', 'h3'
        self._heading_depth = 0
        self.raw_html = ""

    def feed_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        self.raw_html = content
        # Check for data-modal
        self.has_data_modal = 'data-modal' in content
        self.has_call = '7876645040' in content or '(787) 664-5040' in content
        self.has_whatsapp = 'wa.me/17876645040' in content
        self.feed(content)

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag == 'title':
            self._current_tag = 'title'
            self._current_text = ""
        elif tag in ('h1', 'h2', 'h3'):
            self._in_heading = tag
            self._heading_depth += 1
            self._current_text = ""
        elif tag == 'meta':
            name = attrs_dict.get('name', '').lower()
            if name == 'description':
                self.meta_desc = attrs_dict.get('content', '')
        elif tag == 'link':
            rel = attrs_dict.get('rel', '')
            href = attrs_dict.get('href', '')
            if rel == 'canonical':
                self.canonical = href
            if href:
                self.links.append(href)
        elif tag == 'a':
            href = attrs_dict.get('href', '')
            if href:
                self.links.append(href)
        elif tag == 'img':
            src = attrs_dict.get('src', '')
            alt = attrs_dict.get('alt', '')
            self.images.append({'src': src, 'alt': alt})

    def handle_endtag(self, tag):
        if tag == 'title' and self._current_tag == 'title':
            self.title = self._current_text.strip()
            self._current_tag = None
        elif tag in ('h1', 'h2', 'h3') and self._in_heading == tag:
            self._heading_depth -= 1
            if self._heading_depth <= 0:
                text = decode_entities(self._current_text)
                if text:
                    if tag == 'h1':
                        self.h1s.append(text)
                    elif tag == 'h2':
                        self.h2s.append(text)
                    elif tag == 'h3':
                        self.h3s.append(text)
                self._in_heading = None
                self._heading_depth = 0

    def handle_data(self, data):
        if self._current_tag == 'title':
            self._current_text += data
        if self._in_heading:
            self._current_text += data


def normalize(text):
    """Normalize for comparison: decode entities, collapse whitespace."""
    return decode_entities(text)


def check_heading_match(expected_list, found_list, label):
    """Check that every expected heading appears in found list."""
    if not expected_list:
        return True, [], found_list

    missing = []
    for exp in expected_list:
        exp_norm = normalize(exp)
        found = False
        for f in found_list:
            f_norm = normalize(f)
            if exp_norm.lower() == f_norm.lower():
                found = True
                break
            # Also try substring match
            if exp_norm.lower() in f_norm.lower() or f_norm.lower() in exp_norm.lower():
                found = True
                break
        if not found:
            missing.append(exp)

    return len(missing) == 0, missing, found_list


def main():
    with open(SEO_REF, 'r', encoding='utf-8') as f:
        seo_data = json.load(f)

    # Results tracking
    all_results = {}
    check_names = [
        "Filename", "Title", "Meta desc", "H1", "H2", "H3",
        "Images", "Image alts", "Internal links", "Booking modal", "Canonical"
    ]

    for entry in seo_data:
        filename = entry['filename']

        # Determine file path
        if filename.startswith('blog/'):
            filepath = os.path.join(OUTPUT, filename)
        else:
            filepath = os.path.join(OUTPUT, filename)

        print(f"\n{'='*10} {filename} {'='*10}")

        results = {}

        # 1. Filename check
        if os.path.exists(filepath):
            results["Filename"] = True
            print(f"1. Filename: ✅")
        else:
            results["Filename"] = False
            print(f"1. Filename: ❌ (file not found: {filepath})")
            # Fill remaining as False
            for c in check_names[1:]:
                results[c] = False
                print(f"   {c}: ❌ (file missing)")
            all_results[filename] = results
            continue

        # Parse HTML
        extractor = HTMLExtractor()
        try:
            extractor.feed_file(filepath)
        except Exception as e:
            print(f"   Parse error: {e}")
            for c in check_names[1:]:
                results[c] = False
            all_results[filename] = results
            continue

        # 2. Title
        exp_title = normalize(entry.get('title', ''))
        found_title = normalize(extractor.title)
        if exp_title == found_title:
            results["Title"] = True
            print(f"2. Title: ✅")
        else:
            results["Title"] = False
            print(f"2. Title: ❌")
            print(f"   expected: \"{exp_title}\"")
            print(f"   found:    \"{found_title}\"")

        # 3. Meta description
        exp_desc = normalize(entry.get('meta_description', ''))
        found_desc = normalize(extractor.meta_desc)
        if exp_desc == found_desc:
            results["Meta desc"] = True
            print(f"3. Meta desc: ✅")
        else:
            results["Meta desc"] = False
            print(f"3. Meta desc: ❌")
            print(f"   expected: \"{exp_desc}\"")
            print(f"   found:    \"{found_desc}\"")

        # 4. H1
        exp_h1 = entry.get('headings', {}).get('h1', [])
        ok, missing, found = check_heading_match(exp_h1, extractor.h1s, 'h1')
        if ok:
            results["H1"] = True
            print(f"4. H1: ✅")
        else:
            results["H1"] = False
            print(f"4. H1: ❌")
            print(f"   expected: {exp_h1}")
            print(f"   found:    {found}")
            print(f"   missing:  {missing}")

        # 5. H2
        exp_h2 = entry.get('headings', {}).get('h2', [])
        ok, missing, found = check_heading_match(exp_h2, extractor.h2s, 'h2')
        if ok:
            results["H2"] = True
            print(f"5. H2: ✅")
        else:
            results["H2"] = False
            print(f"5. H2: ❌")
            print(f"   expected: {exp_h2}")
            print(f"   missing:  {missing}")
            print(f"   found:    {found}")

        # 6. H3
        exp_h3 = entry.get('headings', {}).get('h3', [])
        ok, missing, found = check_heading_match(exp_h3, extractor.h3s, 'h3')
        if ok:
            results["H3"] = True
            print(f"6. H3: ✅")
        else:
            results["H3"] = False
            print(f"6. H3: ❌")
            print(f"   expected: {exp_h3}")
            print(f"   missing:  {missing}")
            print(f"   found:    {found}")

        # 7. Images (src matching)
        exp_images = entry.get('images', [])
        found_srcs = {img['src'] for img in extractor.images}
        missing_srcs = []
        for img in exp_images:
            if img['src'] not in found_srcs:
                missing_srcs.append(img['src'])
        if not missing_srcs:
            results["Images"] = True
            print(f"7. Images: ✅ (expected: {len(exp_images)}, found: {len(extractor.images)})")
        else:
            results["Images"] = False
            print(f"7. Images: ❌ (expected: {len(exp_images)}, found: {len(extractor.images)})")
            print(f"   missing src: {missing_srcs}")

        # 8. Image alts
        exp_alt_map = {img['src']: img['alt'] for img in exp_images}
        found_alt_map = {}
        for img in extractor.images:
            found_alt_map[img['src']] = img['alt']

        mismatched_alts = []
        for src, exp_alt in exp_alt_map.items():
            if src in found_alt_map:
                found_alt = found_alt_map[src]
                if normalize(exp_alt) != normalize(found_alt):
                    mismatched_alts.append({
                        'src': src,
                        'expected': exp_alt,
                        'found': found_alt
                    })

        if not mismatched_alts:
            results["Image alts"] = True
            print(f"8. Image alts: ✅")
        else:
            results["Image alts"] = False
            print(f"8. Image alts: ❌ ({len(mismatched_alts)} mismatched)")
            for m in mismatched_alts[:5]:  # show first 5
                print(f"   src: {m['src']}")
                print(f"     expected alt: \"{m['expected']}\"")
                print(f"     found alt:    \"{m['found']}\"")
            if len(mismatched_alts) > 5:
                print(f"   ... and {len(mismatched_alts) - 5} more")

        # 9. Internal links
        exp_links = entry.get('internal_links', [])
        found_links_set = set(extractor.links)
        missing_links = []
        for link in exp_links:
            if link not in found_links_set:
                # Try some variations
                found = False
                for fl in found_links_set:
                    if fl == link or fl.rstrip('/') == link.rstrip('/'):
                        found = True
                        break
                if not found:
                    missing_links.append(link)

        if not missing_links:
            results["Internal links"] = True
            print(f"9. Internal links: ✅ (expected: {len(exp_links)}, found in page: {len(found_links_set)})")
        else:
            results["Internal links"] = False
            print(f"9. Internal links: ❌ (expected: {len(exp_links)}, missing: {len(missing_links)})")
            for ml in missing_links:
                print(f"   missing: {ml}")

        # 10. Booking modal
        dm = extractor.has_data_modal
        call = extractor.has_call
        wa = extractor.has_whatsapp
        if dm and call and wa:
            results["Booking modal"] = True
            print(f"10. Booking modal: ✅")
        else:
            results["Booking modal"] = False
            print(f"10. Booking modal: ❌ (data-modal: {'Y' if dm else 'N'}, call: {'Y' if call else 'N'}, whatsapp: {'Y' if wa else 'N'})")

        # 11. Canonical
        exp_canonical = entry.get('canonical', '')
        # Also check internal_links for canonical URL pattern
        if not exp_canonical:
            # Try to find canonical in internal_links
            for link in exp_links:
                if link.startswith('https://miamiyachtcollective.com/'):
                    exp_canonical = link
                    break

        found_canonical = extractor.canonical
        if exp_canonical and found_canonical:
            if exp_canonical == found_canonical:
                results["Canonical"] = True
                print(f"11. Canonical: ✅")
            else:
                results["Canonical"] = False
                print(f"11. Canonical: ❌")
                print(f"    expected: \"{exp_canonical}\"")
                print(f"    found:    \"{found_canonical}\"")
        elif not exp_canonical and not found_canonical:
            results["Canonical"] = True
            print(f"11. Canonical: ✅ (none expected, none found)")
        elif not exp_canonical:
            # No expected canonical in seo-reference; having one is OK
            results["Canonical"] = True
            print(f"11. Canonical: ✅ (no canonical in seo-ref, found: \"{found_canonical}\")")
        else:
            results["Canonical"] = False
            print(f"11. Canonical: ❌ (expected: \"{exp_canonical}\", found: none)")

        all_results[filename] = results

    # Summary table
    print("\n\n" + "=" * 120)
    print("SUMMARY TABLE")
    print("=" * 120)

    # Header
    header = f"{'Page':<45}"
    for c in check_names:
        short = c[:8]
        header += f" {short:>8}"
    print(header)
    print("-" * 120)

    total_pass = {c: 0 for c in check_names}
    total_fail = {c: 0 for c in check_names}

    for filename in sorted(all_results.keys()):
        row = f"{filename:<45}"
        for c in check_names:
            val = all_results[filename].get(c, None)
            if val is True:
                row += f" {'✅':>8}"
                total_pass[c] += 1
            elif val is False:
                row += f" {'❌':>8}"
                total_fail[c] += 1
            else:
                row += f" {'?':>8}"
        print(row)

    print("-" * 120)
    total_row = f"{'PASS/TOTAL':<45}"
    total_pages = len(all_results)
    for c in check_names:
        total_row += f" {total_pass[c]:>3}/{total_pages:<4}"
    print(total_row)

    # Overall
    total_checks = sum(total_pass.values()) + sum(total_fail.values())
    total_passed = sum(total_pass.values())
    print(f"\nOVERALL: {total_passed}/{total_checks} checks passed ({total_passed*100//total_checks}%)")

    # List pages with failures
    failing_pages = [f for f, r in all_results.items() if any(v is False for v in r.values())]
    if failing_pages:
        print(f"\nPages with failures ({len(failing_pages)}):")
        for fp in sorted(failing_pages):
            fails = [c for c in check_names if all_results[fp].get(c) is False]
            print(f"  {fp}: {', '.join(fails)}")
    else:
        print("\nAll pages passed all checks! 🎉")


if __name__ == '__main__':
    main()
