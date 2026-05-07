UPDATE public.articles SET hero_image_url = CASE id
  WHEN 14 THEN 'https://images.theconversation.com/files/731660/original/file-20260422-57-37cezx.jpg?ixlib=rb-4.1.0&rect=0%2C504%2C4032%2C2016&q=45&auto=format&w=1356&h=668&fit=crop'
  WHEN 15 THEN 'https://images.theconversation.com/files/733432/original/file-20260501-57-i8kiyk.jpg?ixlib=rb-4.1.0&rect=0%2C758%2C7968%2C3984&q=45&auto=format&w=1356&h=668&fit=crop'
  WHEN 16 THEN 'https://images.theconversation.com/files/732190/original/file-20260424-57-ovduw0.jpg?ixlib=rb-4.1.0&rect=0%2C100%2C1280%2C640&q=45&auto=format&w=1356&h=668&fit=crop'
  WHEN 17 THEN 'https://images.theconversation.com/files/731355/original/file-20260421-57-635mw0.png?ixlib=rb-4.1.0&rect=0%2C88%2C1201%2C600&q=45&auto=format&w=1356&h=668&fit=crop'
  WHEN 18 THEN 'https://images.theconversation.com/files/732962/original/file-20260429-69-yrnznx.jpg?ixlib=rb-4.1.0&rect=0%2C881%2C5280%2C2640&q=45&auto=format&w=1356&h=668&fit=crop'
  WHEN 29 THEN 'https://images.theconversation.com/files/719787/original/file-20260223-56-rx0phi.jpg?ixlib=rb-4.1.0&rect=0%2C514%2C6541%2C3270&q=45&auto=format&w=1356&h=668&fit=crop'
  WHEN 30 THEN 'https://images.theconversation.com/files/718216/original/file-20260213-56-19x31e.jpg?ixlib=rb-4.1.0&rect=0%2C722%2C5525%2C2762&q=45&auto=format&w=1356&h=668&fit=crop'
  WHEN 33 THEN 'https://images.theconversation.com/files/712500/original/file-20260114-56-wcwibo.jpg?ixlib=rb-4.1.0&rect=0%2C252%2C5196%2C2598&q=45&auto=format&w=1356&h=668&fit=crop'
  WHEN 38 THEN 'https://images.theconversation.com/files/701378/original/file-20251110-56-kquxud.jpg?ixlib=rb-4.1.0&rect=0%2C0%2C4032%2C2016&q=45&auto=format&w=1356&h=668&fit=crop'
END
WHERE id IN (14,15,16,17,18,29,30,33,38);