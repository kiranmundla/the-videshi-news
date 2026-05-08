update public.articles
set image_caption = null, image_verified = false
where is_published = true;