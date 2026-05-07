update story_queue
set status = 'failed', error_message = 'max attempts reached'
where status in ('writing', 'enriching', 'editing')
and attempts >= 3
and updated_at < now() - interval '30 minutes';

update story_queue
set status = 'pending', attempts = 0, error_message = null
where error_message like '%JSON%'
or error_message like '%Expected%';