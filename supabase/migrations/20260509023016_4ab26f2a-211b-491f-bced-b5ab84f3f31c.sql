UPDATE public.p2_articles
SET
  headline = btrim(regexp_replace(regexp_replace(regexp_replace(regexp_replace(headline, '<cite[^>]*>([\s\S]*?)</cite>', '\1', 'gi'), '\s*\[\d+(?:[–\-]\d+)?\]', '', 'g'), '</?cite[^>]*>', '', 'gi'), '  +', ' ', 'g')),
  subheadline = CASE WHEN subheadline IS NULL THEN NULL ELSE btrim(regexp_replace(regexp_replace(regexp_replace(regexp_replace(subheadline, '<cite[^>]*>([\s\S]*?)</cite>', '\1', 'gi'), '\s*\[\d+(?:[–\-]\d+)?\]', '', 'g'), '</?cite[^>]*>', '', 'gi'), '  +', ' ', 'g')) END,
  body = btrim(regexp_replace(regexp_replace(regexp_replace(regexp_replace(body, '<cite[^>]*>([\s\S]*?)</cite>', '\1', 'gi'), '\s*\[\d+(?:[–\-]\d+)?\]', '', 'g'), '</?cite[^>]*>', '', 'gi'), '  +', ' ', 'g')),
  diaspora_angle = CASE WHEN diaspora_angle IS NULL THEN NULL ELSE btrim(regexp_replace(regexp_replace(regexp_replace(regexp_replace(diaspora_angle, '<cite[^>]*>([\s\S]*?)</cite>', '\1', 'gi'), '\s*\[\d+(?:[–\-]\d+)?\]', '', 'g'), '</?cite[^>]*>', '', 'gi'), '  +', ' ', 'g')) END
WHERE
  headline ~* '<cite|\[\d+([–\-]\d+)?\]'
  OR (subheadline IS NOT NULL AND subheadline ~* '<cite|\[\d+([–\-]\d+)?\]')
  OR body ~* '<cite|\[\d+([–\-]\d+)?\]'
  OR (diaspora_angle IS NOT NULL AND diaspora_angle ~* '<cite|\[\d+([–\-]\d+)?\]');