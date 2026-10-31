#!/usr/bin/env python3
"""corpus_replay.py — replay the image-rebuild failure corpus
against the NEW (shadow) sourcing path, offline and deterministic.

Corpus: ~/workspace/research_notes/image-rebuild-2026-10-30/
failure-corpus.json — 123 evidenced wrong-image incidents,
Oct 24–30. For each incident this asks, FROM THE RECORD ALONE:

  (a) REJECTION — would the new path have kept the wrong image
      out? Mechanisms, in the order they are tested:
        corpus-blocklist      the wrong file is on the resolved
                              entity's corpus blocklist (canonical
                              file key, or the file's distinctive
                              name tokens in the record's text);
        canonical-p18         NO — this is the still-wrong case:
                              the wrong file IS the intended
                              entity's own P18 (the path would
                              serve it too);
        ambiguous-abstention  the subject name is a same-name
                              registry pair and the record's own
                              context does not discriminate — the
                              new path abstains (decision none), so
                              the wrong image is not served;
        non-visual-entity     language/non-visual subject class;
        canonical-dedup       duplicate-insertion class — one
                              decision path + canonical file-key
                              ledger makes serving the same file
                              twice impossible by construction;
        route-abolition       the wrong image arrived via a route
                              that no longer exists (og:image /
                              outlet branding for that class;
                              the open-search INLINE route for all
                              inlines; open metadata search /
                              Pexels / YouTube-thumb / og:image
                              for heroes, cards and reel extras),
                              and it is not in the new path's
                              candidate set for the adjudicated
                              subject ({P18} ∪ depicts(QID) —
                              a file depicting something else
                              cannot carry a depicts statement
                              for the intended QID);
        confusable-adjudication  sharper form of the above: the
                              record shows the wrong file belongs
                              to a named confusable of the
                              adjudicated subject;
        no-identity-anchor    the adjudicated subject has no QID
                              and no P18 — the new path returns
                              none, so the wrong image (an open-
                              search product) is not served.
      Anything that cannot be decided from the record is marked
      not_replayable WITH the reason — never guessed.

  (b) RECALL — where the corpus records a correct image existed
      or was kept (explicit signals: "swapped in", "kept",
      "fixed in-run"), and more broadly for every incident with
      an adjudicated subject: does the registry give the new
      path a plausible correct image? found_p18 (P18 passes the
      shared quality screen at registry-recorded width) >
      found_depicts_plausible (QID present; depicts availability
      is a live-API fact, not recorded offline) >
      found_p18_unverified (P18 exists, width unrecorded) >
      not_found.

OFFLINE BY DESIGN: no network, no er.resolve (it would cache
back into the registry) — registry-only adjudication reuses
er._candidates / er._hint_score / er._from_entry, and the
quality screen is verified_sourcer.screen_candidate, so the
replay measures the same logic the shadow path runs.

Usage: python3 corpus_replay.py [--corpus PATH] [--out PATH]
Prints the summary + the still-wrong list; writes the full
report JSON (default: the research folder's
corpus-replay-report.json).
"""

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import entity_resolve as er
import verified_sourcer as vs

DEFAULT_CORPUS = (HERE.parent.parent / "research_notes"
                  / "image-rebuild-2026-10-30" / "failure-corpus.json")
DEFAULT_OUT = (HERE.parent.parent / "research_notes"
               / "image-rebuild-2026-10-30" / "corpus-replay-report.json")

_STEM_STOP = {"the", "and", "with", "hon", "jpg", "jpeg", "png",
              "svg", "file", "at", "in", "on", "of"}


def _tokens(text):
    return set(re.findall(r"[a-z0-9]+", str(text or "").lower()))


def _stem_tokens(file_ref):
    key = er.file_key(file_ref)
    if not key:
        return set()
    stem = key.rsplit(".", 1)[0]
    return {t for t in re.findall(r"[a-z0-9]+", stem)
            if len(t) >= 3 and t not in _STEM_STOP}


def _name_in_text(name, text_lower):
    if not name or len(name.strip()) < 3:
        return False
    pat = r"(?<![a-z0-9])" + re.escape(name.lower()) + r"(?![a-z0-9])"
    return re.search(pat, text_lower) is not None


def match_entries(text, reg):
    """Registry entries whose name or alias appears in text.
    Returns [(entry, matched_name)]."""
    tl = str(text or "").lower()
    out = []
    for e in reg["entities"]:
        for nm in [e.get("name")] + list(e.get("aliases") or []):
            if nm and _name_in_text(nm, tl):
                out.append((e, nm))
                break
    return out


def adjudicate(matches, intent_context):
    """Split matches into (intended_entries, ambiguous_flag).
    Same matched string hitting >1 entry = a namesake group,
    adjudicated by registry context hints against the record's
    own statement of intent; a tie stays ambiguous (the new path
    abstains rather than guesses)."""
    groups = {}
    for e, nm in matches:
        groups.setdefault(er._norm(nm), []).append(e)
    intended, ambiguous = [], False
    for g in groups.values():
        if len(g) == 1:
            intended.append(g[0])
            continue
        scored = sorted(g, key=lambda e: -er._hint_score(
            e, intent_context))
        top = er._hint_score(scored[0], intent_context)
        second = er._hint_score(scored[1], intent_context)
        if top > second:
            intended.append(scored[0])
        else:
            ambiguous = True
    return intended, ambiguous


def _distinctive_tokens(file_ref, entry):
    """A file stem's tokens MINUS the owning entity's own name
    tokens. The name tokens appear in any description of any
    photo of that person/place, so they identify nothing; the
    remaining tokens are what actually fingerprint THIS file
    (e.g. 'yogi adityanath' for one Srivastava felicitation
    photo vs 'maurya' for its unblocked sibling)."""
    st = _stem_tokens(file_ref)
    name_tokens = set()
    for nm in [entry.get("name")] + list(entry.get("aliases") or []):
        name_tokens |= _tokens(nm)
    return st - name_tokens


def _stem_named_in_text(file_ref, entry, text_tokens):
    """Is this file fingerprinted in the text? Requires: >=2 stem
    tokens present, >=60% of the stem present, AND at least one
    DISTINCTIVE (non-name) token among the hits — a person's name
    alone appears in descriptions of every photo of them, which
    is how the unblocked Maurya felicitation photo must NOT
    fingerprint-match its blocked Yogi sibling. Sole exception:
    when the file name is exactly the entity's own name-form
    (distinctive set empty), the full stem (>=3 tokens) must
    appear verbatim."""
    st = _stem_tokens(file_ref)
    if len(st) < 2:
        return False
    hit = st & text_tokens
    if len(hit) < 2 or len(hit) / len(st) < 0.6:
        return False
    d = _distinctive_tokens(file_ref, entry)
    if d:
        return len(hit & d) >= 1
    return hit == st and len(st) >= 3


def identify_wrong_file(inc, reg, all_matches):
    """Best identification of the wrong file's canonical key from
    the record text. Returns (key, how, owner_entry) — owner is
    the registry entry whose blocked file / P18 the key is, when
    known. (None, None, None) when the record does not identify
    the file."""
    text = " ".join([inc.get("photo_showed") or "",
                     inc.get("note") or "",
                     inc.get("article_descriptor") or ""])
    text_tokens = _tokens(text)
    # 1. a blocked file fingerprinted in the text by its
    #    distinctive (non-name) stem tokens
    for e in reg["entities"]:
        for b in e.get("blocked_files") or []:
            if _stem_named_in_text(b, e, text_tokens):
                return er.file_key(b), "blocked-file named in record", e
    # 2. an explicit filename (quoted or bare) in the text
    for m in re.findall(r"[\w .,'()-]+\.(?:jpg|jpeg|png|svg|webp)",
                        text, flags=re.IGNORECASE):
        k = er.file_key(m)
        if k:
            return k, "filename in record", None
    # 3. a registry P18 fingerprinted by its distinctive tokens
    for e in reg["entities"]:
        if e.get("p18_file") and _stem_named_in_text(
                e["p18_file"], e, text_tokens):
            return er.file_key(e["p18_file"]), \
                "P18 file named in record", e
    return None, None, None


def _p18_passes(entry, blocked_keys):
    """Does this registry entry's P18 pass the shared screen at
    its registry-recorded width (offline: no live lookup)?"""
    p18 = entry.get("p18_file")
    if not p18:
        return False
    w = entry.get("p18_quality")
    ok, _ = vs.screen_candidate(
        p18, w if isinstance(w, int) else None, blocked_keys)
    return ok


def recall_outcome(entries):
    """(outcome, entity_name): found_p18 > found_depicts_plausible
    > found_p18_unverified > not_found, over candidate correct
    entities. (None, None) when there is no entity to judge."""
    if not entries:
        return None, None
    for e in entries:
        bk = {er.file_key(b) for b in e.get("blocked_files") or []
              if er.file_key(b)}
        if _p18_passes(e, bk):
            return "found_p18", e["name"]
    for e in entries:
        if e.get("wikidata_qid"):
            return "found_depicts_plausible", e["name"]
    for e in entries:
        if e.get("p18_file"):
            return "found_p18_unverified", e["name"]
    return "not_found", entries[0]["name"]


def _confusable_hit(intended, w_owner, photo_text):
    """Name of the confusable the wrong image belongs to, when
    the record shows one: either the identified wrong file IS a
    confusable entry's own P18, or the confusable's distinctive
    name tokens (its name minus the subject's name tokens) all
    appear in the record's description of the photo."""
    if not intended:
        return None
    if w_owner is not None and w_owner not in intended:
        for e in intended:
            conf_names = {er._norm(c.get("name"))
                          for c in e.get("confusables") or []}
            shared_alias = ({er._norm(a) for a in
                             w_owner.get("aliases") or []}
                            & {er._norm(a) for a in
                               e.get("aliases") or []})
            if er._norm(w_owner["name"]) in conf_names \
                    or shared_alias:
                return w_owner["name"]
    photo_tokens = _tokens(photo_text)
    for e in intended:
        subj_tokens = _tokens(e.get("name"))
        for c in e.get("confusables") or []:
            left = _tokens(c.get("name")) - subj_tokens
            if not left:
                continue
            present = left & photo_tokens
            need = max(1, min(2, len(left)))
            if len(present) >= need \
                    and len(present) / len(left) >= 0.5:
                return c.get("name")
    return None


_EXPLICIT_SIGNALS = ("swapped in", "kept", "fixed in-run")


def replay(corpus, reg):
    results = []
    for inc in corpus["incidents"]:
        surface = inc.get("surface")
        cls = inc.get("failure_class")
        story_text = " ".join([
            inc.get("article_descriptor") or "",
            (inc.get("article_slug") or "").replace("-", " ")])
        should = inc.get("should_have_been") or ""
        intent_ctx = story_text + " " + should
        story_matches = match_entries(story_text, reg)
        intended, ambiguous = adjudicate(story_matches, intent_ctx)
        if not intended and not ambiguous:
            # the fix text sometimes names the subject the record's
            # descriptor doesn't (e.g. the TCS swap-in case)
            fb = match_entries(should, reg)
            if fb:
                intended, ambiguous = adjudicate(fb, intent_ctx)
        all_matches = match_entries(
            story_text + " " + should + " "
            + (inc.get("photo_showed") or ""), reg)
        all_entries = [e for e, _ in all_matches]
        W, w_how, w_owner = identify_wrong_file(inc, reg,
                                                all_entries)
        blocked_keys_all = set()
        for e in all_entries:
            blocked_keys_all |= {er.file_key(b)
                                 for b in e.get("blocked_files") or []
                                 if er.file_key(b)}
        cand_keys = {er.file_key(e["p18_file"]) for e in intended
                     if e.get("p18_file")
                     and er.file_key(e["p18_file"])}
        conf_hit = _confusable_hit(intended, w_owner,
                                   inc.get("photo_showed") or "") \
            if intended else None
        det, mech, reason = None, None, ""
        if W and W in blocked_keys_all:
            det, mech = "rejected", "corpus-blocklist"
            reason = (f"wrong file '{W}' is on a corpus blocklist "
                      f"({w_how}) — the shared screen rejects it "
                      f"for every surface")
        elif W and W in cand_keys:
            owner_e = next(e for e in intended
                           if er.file_key(e.get("p18_file") or "")
                           == W)
            bk = {er.file_key(b)
                  for b in owner_e.get("blocked_files") or []
                  if er.file_key(b)}
            if _p18_passes(owner_e, bk):
                det, mech = "still_wrong", \
                    "canonical-p18-is-the-wrong-file"
                reason = (f"the wrong file IS {owner_e['name']}'s "
                          f"own P18 and it passes the quality "
                          f"screen — identity-by-construction "
                          f"serves it too; only a registry data "
                          f"correction (or the vision triage "
                          f"layer) catches this")
            else:
                det, mech = "rejected", "quality-screen"
                reason = (f"the wrong file is {owner_e['name']}'s "
                          f"own P18, but that P18 fails the "
                          f"quality screen (logo/width/blocklist) "
                          f"— the new path screens it out and "
                          f"falls through to depicts/none")
        elif conf_hit:
            det, mech = "rejected", "confusable-adjudication"
            reason = (f"wrong image belongs to confusable "
                      f"'{conf_hit}' of adjudicated subject "
                      f"{intended[0]['name']} — resolution is "
                      f"adjudicated by context, and P18/depicts "
                      f"are taken only for the intended QID")
        elif not intended and ambiguous:
            det, mech = "rejected", "ambiguous-abstention"
            reason = ("subject name is a same-name registry pair "
                      "and the record's context does not "
                      "discriminate — new path abstains (none), "
                      "wrong image not served")
        elif cls == "language/non-visual entity":
            det, mech = "rejected", "non-visual-entity"
            reason = ("language subjects are non-visual in the new "
                      "path (registry type 'language'; no photo is "
                      "ever sourced for them)")
        elif cls == "duplicate-insertion":
            det, mech = "rejected", "canonical-dedup"
            reason = ("one decision path + canonical file-key "
                      "ledger: the same file cannot be placed "
                      "twice on one article by construction")
        elif cls == "outlet-branding":
            det, mech = "rejected", "route-abolition"
            reason = ("og:image / outlet-graphic route abolished; "
                      "identity rungs never return outlet branding")
        elif surface == "inline":
            det, mech = "rejected", "inline-route-abolition"
            reason = ("the open-search inline route is abolished; "
                      "new inlines come only from Rungs 1–3 for "
                      "subjects/co-subjects, and this file is not "
                      "in the adjudicated subject's candidate set")
        elif intended:
            if all(not e.get("wikidata_qid")
                   and not e.get("p18_file") for e in intended):
                det, mech = "rejected", "no-identity-anchor"
                reason = ("adjudicated subject "
                          + ", ".join(e["name"] for e in intended)
                          + " has no QID and no P18 — new path "
                          "returns none; the wrong image was an "
                          "open-search product")
            else:
                det, mech = "rejected", "route-abolition"
                reason = ("wrong image arrived via an abolished "
                          "open route and is not in the "
                          "adjudicated subject's candidate set "
                          "({P18} ∪ depicts(QID))")
        else:
            det, mech = "not_replayable", None
            reason = ("story subject is not identifiable in the "
                      "registry from the record (descriptor/slug/"
                      "fix text name no registered entity, and no "
                      "blocklist hit) — the outcome would depend "
                      "on live resolution, which the record "
                      "cannot adjudicate")
            if all_entries:
                names = ", ".join(sorted({e["name"]
                                          for e in all_entries}))
                reason += (f" Record does name registered "
                           f"entities ({names}) — as the wrong "
                           f"photo's subject or in passing — but "
                           f"no adjudicable story subject or "
                           f"blocked-file identification follows "
                           f"from the record")
                if any(e.get("blocked_files")
                       for e in all_entries):
                    reason += ("; a matched entity carries "
                               "blocked files, but the record's "
                               "wrong file is not identifiable as "
                               "one of them (a sibling file is "
                               "not a blocklist hit)")
        explicit = any(s in (should + " " + (inc.get("note")
                                              or "")).lower()
                       for s in _EXPLICIT_SIGNALS)
        rec_entries = list(intended)
        fb_intended, _ = adjudicate(match_entries(should, reg),
                                    intent_ctx)
        for e in fb_intended:
            if e not in rec_entries:
                rec_entries.append(e)
        rec, rec_entity = recall_outcome(rec_entries)
        if rec is None and explicit:
            rec = "not_assessable"
        results.append({
            "id": inc.get("id"),
            "surface": surface,
            "failure_class": cls,
            "slug": inc.get("article_slug"),
            "descriptor": inc.get("article_descriptor"),
            "determination": det,
            "mechanism": mech,
            "reason": reason,
            "wrong_file_key": W,
            "wrong_file_how": w_how,
            "intended_entities": [e["name"] for e in intended],
            "explicit_correct_existed": explicit,
            "recall": rec,
            "recall_entity": rec_entity,
        })
    return results


def summarize(results):
    total = len(results)
    rej = [r for r in results if r["determination"] == "rejected"]
    sw = [r for r in results if r["determination"] == "still_wrong"]
    nr = [r for r in results
          if r["determination"] == "not_replayable"]
    replayable = total - len(nr)
    expl = [r for r in results if r["explicit_correct_existed"]]
    by_ent = [r for r in results if r["intended_entities"]]
    from collections import Counter
    return {
        "total": total,
        "rejected": len(rej),
        "still_wrong": len(sw),
        "not_replayable": len(nr),
        "replayable": replayable,
        "rejected_pct_of_replayable":
            round(100.0 * len(rej) / replayable, 1) if replayable
            else None,
        "rejected_pct_of_all":
            round(100.0 * len(rej) / total, 1) if total else None,
        "mechanisms": dict(Counter(r["mechanism"] for r in rej)),
        "recall_over_adjudicated_subjects": dict(Counter(
            r["recall"] for r in by_ent)),
        "recall_p18_confirmed_pct":
            round(100.0 * sum(1 for r in by_ent
                              if r["recall"] == "found_p18")
                  / len(by_ent), 1) if by_ent else None,
        "recall_incl_depicts_plausible_pct":
            round(100.0 * sum(1 for r in by_ent
                              if r["recall"] in
                              ("found_p18",
                               "found_depicts_plausible"))
                  / len(by_ent), 1) if by_ent else None,
        "explicit_correct_existed_cases": [
            {"id": r["id"], "recall": r["recall"],
             "intended_entities": r["intended_entities"]}
            for r in expl],
        "still_wrong_ids": [r["id"] for r in sw],
        "not_replayable_ids": [r["id"] for r in nr],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args(argv)
    with open(args.corpus) as f:
        corpus = json.load(f)
    reg = er.load_registry()
    results = replay(corpus, reg)
    summary = summarize(results)
    report = {
        "summary": summary,
        "limits": [
            "Offline replay: depicts() availability is a live-API "
            "fact. Recall counts a QID as 'depicts plausible', "
            "not as files verified to exist.",
            "Rejection via route-abolition assumes a wrong file "
            "cannot carry a depicts(P180) statement for the "
            "intended QID. A Commons depicts data error (a file "
            "wrongly tagged as depicting the subject) would pass "
            "the new path and is invisible to this replay — that "
            "residual class belongs to the vision-triage layer.",
            "Cases whose story subject is not in the registry are "
            "marked not_replayable rather than extrapolated from "
            "live-resolution behaviour.",
            "The wrong file is positively identified from the "
            "record in a minority of cases; where it is not, "
            "rejection rests on the candidate-set argument "
            "({P18} ∪ depicts(QID)) plus the abolished route, "
            "both stated per incident.",
        ],
        "incidents": results,
    }
    if args.out:
        with open(args.out, "w") as f:
            json.dump(report, f, indent=1, ensure_ascii=False)
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    sw = [r for r in results if r["determination"] == "still_wrong"]
    if sw:
        print("\nSTILL WRONG under the new path:")
        for r in sw:
            print(f"  #{r['id']} [{r['surface']}/{r['failure_class']}]"
                  f" {r['descriptor']}\n      {r['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
