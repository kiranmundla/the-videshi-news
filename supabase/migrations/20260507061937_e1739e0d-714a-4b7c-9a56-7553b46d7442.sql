update public.articles
set
  body = regexp_replace(body, '</?cite[^>]*>', '', 'gi'),
  summary = regexp_replace(summary, '</?cite[^>]*>', '', 'gi'),
  nri_angle = case when nri_angle is null then null
    else regexp_replace(nri_angle, '</?cite[^>]*>', '', 'gi')
  end;