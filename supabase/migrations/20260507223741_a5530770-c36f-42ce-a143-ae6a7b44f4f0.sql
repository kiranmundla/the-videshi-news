UPDATE articles
SET body = regexp_replace(
  body,
  'Looking at the format from what you pasted earlier.*?Here''s the exact same content formatted to match:\n\n',
  '',
  'gs'
)
WHERE id = 'f3c98ec9-239e-4620-a8f4-a3c4b4e8c1f4';