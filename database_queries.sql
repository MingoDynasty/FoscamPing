-- Get a latest ping result for each device.
Select p.device_id, p.date_pinged, packets_sent, packets_received, packets_lost, minimum_ping, maximum_ping, average_ping, is_success 
From ping_results p Inner Join (Select device_id, max(DATE_PINGED) as DATE_PINGED From ping_results Group By device_id) q 
On p.device_id = q.device_id And p.DATE_PINGED = q.DATE_PINGED
