
insert into storage.buckets (id, name, public)
values ('article-images', 'article-images', true)
on conflict (id) do update set public = true;

create policy "Public read article-images"
on storage.objects for select
using (bucket_id = 'article-images');

create policy "Service role write article-images"
on storage.objects for insert
with check (bucket_id = 'article-images' and auth.role() = 'service_role');

create policy "Service role update article-images"
on storage.objects for update
using (bucket_id = 'article-images' and auth.role() = 'service_role');
