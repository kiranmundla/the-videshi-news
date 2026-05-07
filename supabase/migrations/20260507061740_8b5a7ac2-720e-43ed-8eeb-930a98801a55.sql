update public.articles
set
  body = regexp_replace(regexp_replace(body, '</?cite\b[^>]*>', '', 'gi'), '\[\d+(?:[-,\s]\d+)*\]', '', 'g'),
  summary = regexp_replace(regexp_replace(summary, '</?cite\b[^>]*>', '', 'gi'), '\[\d+(?:[-,\s]\d+)*\]', '', 'g'),
  nri_angle = case when nri_angle is null then null
    else regexp_replace(regexp_replace(nri_angle, '</?cite\b[^>]*>', '', 'gi'), '\[\d+(?:[-,\s]\d+)*\]', '', 'g')
  end;