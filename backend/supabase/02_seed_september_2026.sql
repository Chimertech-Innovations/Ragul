-- =====================================================================
-- RAGUL AI - GREEN VALLEY DAIRY FARM (FARM_DEMO_001)
-- COMPLETE 30-DAY TELEMETRY DATASET (SEPTEMBER 1 - SEPTEMBER 30, 2026)
-- =====================================================================

INSERT INTO farms (id, name, location, timezone, total_cameras)
VALUES ('FARM_DEMO_001', 'Green Valley Dairy Farm', 'Tamil Nadu, India', 'Asia/Kolkata', 6)
ON CONFLICT (id) DO NOTHING;

INSERT INTO cctv_cameras (camera_id, farm_id, coverage_zone)
VALUES ('CAM01', 'FARM_DEMO_001', 'Main gate and worker entry')
ON CONFLICT (camera_id) DO NOTHING;
INSERT INTO cctv_cameras (camera_id, farm_id, coverage_zone)
VALUES ('CAM02', 'FARM_DEMO_001', 'Milking parlour')
ON CONFLICT (camera_id) DO NOTHING;
INSERT INTO cctv_cameras (camera_id, farm_id, coverage_zone)
VALUES ('CAM03', 'FARM_DEMO_001', 'Pen 1 - lactating cows')
ON CONFLICT (camera_id) DO NOTHING;
INSERT INTO cctv_cameras (camera_id, farm_id, coverage_zone)
VALUES ('CAM04', 'FARM_DEMO_001', 'Pen 2 - dry/heifer cows')
ON CONFLICT (camera_id) DO NOTHING;
INSERT INTO cctv_cameras (camera_id, farm_id, coverage_zone)
VALUES ('CAM05', 'FARM_DEMO_001', 'Feed alley and water trough')
ON CONFLICT (camera_id) DO NOTHING;
INSERT INTO cctv_cameras (camera_id, farm_id, coverage_zone)
VALUES ('CAM06', 'FARM_DEMO_001', 'Calving/isolation area')
ON CONFLICT (camera_id) DO NOTHING;

INSERT INTO workers (worker_id, farm_id, name, role, phone, shift_hours, duties)
VALUES ('W001', 'FARM_DEMO_001', 'Kumar', 'Farm Supervisor', '+91 98421 00100', '05:42 AM - 05:48 PM', 'Farm gate entry, workforce coordination & overall supervisor')
ON CONFLICT (worker_id) DO NOTHING;
INSERT INTO workers (worker_id, farm_id, name, role, phone, shift_hours, duties)
VALUES ('W002', 'FARM_DEMO_001', 'Ravi', 'Feeding Worker', '+91 98421 00200', '05:49 AM - 05:20 PM', 'Morning & evening TMR and green fodder ration distribution in feed alley')
ON CONFLICT (worker_id) DO NOTHING;
INSERT INTO workers (worker_id, farm_id, name, role, phone, shift_hours, duties)
VALUES ('W003', 'FARM_DEMO_001', 'Selvam', 'Milking Worker', '+91 98421 00300', '05:36 AM - 04:45 PM', 'Milking parlour machine operation, yield logging & teat hygiene')
ON CONFLICT (worker_id) DO NOTHING;
INSERT INTO workers (worker_id, farm_id, name, role, phone, shift_hours, duties)
VALUES ('W004', 'FARM_DEMO_001', 'Mani', 'Cleaning Worker', '+91 98421 00400', '05:55 AM - 05:10 PM', 'Pen 1 & Pen 2 dung scraping, floor sanitizing and bed freshening')
ON CONFLICT (worker_id) DO NOTHING;
INSERT INTO workers (worker_id, farm_id, name, role, phone, shift_hours, duties)
VALUES ('W005', 'FARM_DEMO_001', 'Arun', 'General Worker', '+91 98421 00500', '06:02 AM - 05:30 PM', 'General farm maintenance & cleaning relief worker')
ON CONFLICT (worker_id) DO NOTHING;

INSERT INTO cattle (cattle_id, farm_id, rfid, name, pen_group, lactation_status, baseline_daily_yield_litres)
VALUES ('COW001', 'FARM_DEMO_001', '901009000037981', 'Lakshmi', 'Pen 1', 'Lactating', 18.5)
ON CONFLICT (cattle_id) DO NOTHING;
INSERT INTO cattle (cattle_id, farm_id, rfid, name, pen_group, lactation_status, baseline_daily_yield_litres)
VALUES ('COW002', 'FARM_DEMO_001', '901009000037982', 'Nandhini', 'Pen 1', 'Lactating', 18.5)
ON CONFLICT (cattle_id) DO NOTHING;
INSERT INTO cattle (cattle_id, farm_id, rfid, name, pen_group, lactation_status, baseline_daily_yield_litres)
VALUES ('COW003', 'FARM_DEMO_001', '901009000037983', 'Ponni', 'Pen 1', 'Lactating', 18.5)
ON CONFLICT (cattle_id) DO NOTHING;
INSERT INTO cattle (cattle_id, farm_id, rfid, name, pen_group, lactation_status, baseline_daily_yield_litres)
VALUES ('COW004', 'FARM_DEMO_001', '901009000037984', 'Kaveri', 'Pen 1', 'Lactating', 18.5)
ON CONFLICT (cattle_id) DO NOTHING;
INSERT INTO cattle (cattle_id, farm_id, rfid, name, pen_group, lactation_status, baseline_daily_yield_litres)
VALUES ('COW005', 'FARM_DEMO_001', '901009000037985', 'Malli', 'Pen 1', 'Lactating', 18.5)
ON CONFLICT (cattle_id) DO NOTHING;
INSERT INTO cattle (cattle_id, farm_id, rfid, name, pen_group, lactation_status, baseline_daily_yield_litres)
VALUES ('COW006', 'FARM_DEMO_001', '901009000037986', 'Meena', 'Pen 1', 'Lactating', 18.5)
ON CONFLICT (cattle_id) DO NOTHING;
INSERT INTO cattle (cattle_id, farm_id, rfid, name, pen_group, lactation_status, baseline_daily_yield_litres)
VALUES ('COW007', 'FARM_DEMO_001', '901009000037987', 'Selvi', 'Pen 1', 'Lactating', 18.5)
ON CONFLICT (cattle_id) DO NOTHING;
INSERT INTO cattle (cattle_id, farm_id, rfid, name, pen_group, lactation_status, baseline_daily_yield_litres)
VALUES ('COW008', 'FARM_DEMO_001', '901009000037988', 'Roja', 'Pen 2', 'Heifer', 0.0)
ON CONFLICT (cattle_id) DO NOTHING;
INSERT INTO cattle (cattle_id, farm_id, rfid, name, pen_group, lactation_status, baseline_daily_yield_litres)
VALUES ('COW009', 'FARM_DEMO_001', '901009000037989', 'Valli', 'Pen 2', 'Dry', 0.0)
ON CONFLICT (cattle_id) DO NOTHING;
INSERT INTO cattle (cattle_id, farm_id, rfid, name, pen_group, lactation_status, baseline_daily_yield_litres)
VALUES ('COW010', 'FARM_DEMO_001', '901009000037990', 'Ganga', 'Pen 2', 'Pregnant', 0.0)
ON CONFLICT (cattle_id) DO NOTHING;

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-01', 'Tuesday', '5 workers present. Morning and evening feeding recorded. Total milk 127.5 L. Water use 756.2 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 127.5, 756.2, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-01', '2026-09-01T06:35:00+05:30', '2026-09-01T16:05:00+05:30', 127.5)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-01', 'W001', 'Kumar', 'Present', '2026-09-01T05:42:00+05:30', '2026-09-01T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-01', 'W002', 'Ravi', 'Present', '2026-09-01T05:49:00+05:30', '2026-09-01T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-01', 'W003', 'Selvam', 'Present', '2026-09-01T05:36:00+05:30', '2026-09-01T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-01', 'W004', 'Mani', 'Present', '2026-09-01T05:55:00+05:30', '2026-09-01T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-01', 'W005', 'Arun', 'Present', '2026-09-01T06:02:00+05:30', '2026-09-01T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-01', 'COW001', 17.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-01', 'COW002', 19.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-01', 'COW003', 16.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-01', 'COW004', 19.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-01', 'COW005', 16.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-01', 'COW006', 19.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-01', 'COW007', 18.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-01-AM', '2026-09-01', '2026-09-01T06:19:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 124.2, 89.5, 34.9, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-01-PM', '2026-09-01', '2026-09-01T17:00:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 114.9, 85.7, 32.2, 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-01-P1', '2026-09-01', '2026-09-01T08:23:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-01-P2', '2026-09-01', '2026-09-01T09:01:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-01', 'COW001', 2659, 10.2, 458, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-01', 'COW002', 3126, 8.5, 489, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-01', 'COW003', 3121, 8.3, 386, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-01', 'COW004', 3836, 9.7, 471, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-01', 'COW005', 3671, 9.5, 491, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-01', 'COW006', 3179, 9.5, 474, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-01', 'COW007', 3515, 10.3, 444, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-01', 'COW008', 3636, 8.2, 402, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-01', 'COW009', 3055, 8.3, 402, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-01', 'COW010', 2791, 8.8, 451, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-01', 29.1, 72.5, 756.2, 239.1, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-01T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-01T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-01T06:19:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-01T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-01T08:23:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-01T17:00:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-01T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-02', 'Wednesday', '5 workers present. Morning and evening feeding recorded. Total milk 132.1 L. Water use 755.6 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 132.1, 755.6, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-02', '2026-09-02T06:35:00+05:30', '2026-09-02T16:05:00+05:30', 132.1)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-02', 'W001', 'Kumar', 'Present', '2026-09-02T05:42:00+05:30', '2026-09-02T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-02', 'W002', 'Ravi', 'Present', '2026-09-02T05:49:00+05:30', '2026-09-02T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-02', 'W003', 'Selvam', 'Present', '2026-09-02T05:36:00+05:30', '2026-09-02T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-02', 'W004', 'Mani', 'Present', '2026-09-02T05:55:00+05:30', '2026-09-02T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-02', 'W005', 'Arun', 'Present', '2026-09-02T06:02:00+05:30', '2026-09-02T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-02', 'COW001', 18.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-02', 'COW002', 19.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-02', 'COW003', 17.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-02', 'COW004', 21.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-02', 'COW005', 17.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-02', 'COW006', 18.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-02', 'COW007', 18.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-02-AM', '2026-09-02', '2026-09-02T06:14:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 127.3, 88.9, 35.1, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-02-PM', '2026-09-02', '2026-09-02T17:02:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 119.8, 84.5, 30.7, 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-02-P1', '2026-09-02', '2026-09-02T08:17:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-02-P2', '2026-09-02', '2026-09-02T09:05:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-02', 'COW001', 3211, 8.3, 484, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-02', 'COW002', 3444, 10.0, 400, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-02', 'COW003', 3348, 10.4, 452, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-02', 'COW004', 2850, 8.5, 464, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-02', 'COW005', 3404, 10.0, 426, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-02', 'COW006', 3466, 9.0, 494, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-02', 'COW007', 2843, 9.4, 465, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-02', 'COW008', 3855, 8.5, 394, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-02', 'COW009', 3602, 9.7, 421, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-02', 'COW010', 3484, 9.3, 405, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-02', 29.3, 75.9, 755.6, 247.1, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-02T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-02T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-02T06:14:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-02T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-02T08:17:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-02T17:02:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-02T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-03', 'Thursday', '5 workers present. Morning and evening feeding recorded. Total milk 135.4 L. Water use 731.1 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 135.4, 731.1, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-03', '2026-09-03T06:35:00+05:30', '2026-09-03T16:05:00+05:30', 135.4)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-03', 'W001', 'Kumar', 'Present', '2026-09-03T05:42:00+05:30', '2026-09-03T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-03', 'W002', 'Ravi', 'Present', '2026-09-03T05:49:00+05:30', '2026-09-03T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-03', 'W003', 'Selvam', 'Present', '2026-09-03T05:36:00+05:30', '2026-09-03T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-03', 'W004', 'Mani', 'Present', '2026-09-03T05:55:00+05:30', '2026-09-03T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-03', 'W005', 'Arun', 'Present', '2026-09-03T06:02:00+05:30', '2026-09-03T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-03', 'COW001', 19.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-03', 'COW002', 21.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-03', 'COW003', 16.6, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-03', 'COW004', 21.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-03', 'COW005', 17.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-03', 'COW006', 20.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-03', 'COW007', 19.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-03-AM', '2026-09-03', '2026-09-03T06:17:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 130.1, 88.0, 37.5, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 5 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-03-PM', '2026-09-03', '2026-09-03T16:57:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 120.9, 82.1, 31.2, 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-03-P1', '2026-09-03', '2026-09-03T08:24:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-03-P2', '2026-09-03', '2026-09-03T09:00:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-03', 'COW001', 2863, 10.1, 439, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-03', 'COW002', 3740, 9.5, 375, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-03', 'COW003', 3103, 8.2, 486, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-03', 'COW004', 3880, 10.3, 411, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-03', 'COW005', 2731, 10.4, 488, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-03', 'COW006', 2769, 9.4, 383, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-03', 'COW007', 3714, 10.1, 390, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-03', 'COW008', 3315, 9.5, 406, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-03', 'COW009', 3871, 9.2, 400, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-03', 'COW010', 3405, 10.0, 399, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-03', 30.2, 76.5, 731.1, 251.0, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-03T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-03T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-03T06:17:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 5 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-03T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-03T08:24:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-03T16:57:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-03T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-04', 'Friday', '5 workers present. Morning and evening feeding recorded. Total milk 133.4 L. Water use 738.6 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 133.4, 738.6, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-04', '2026-09-04T06:35:00+05:30', '2026-09-04T16:05:00+05:30', 133.4)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-04', 'W001', 'Kumar', 'Present', '2026-09-04T05:42:00+05:30', '2026-09-04T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-04', 'W002', 'Ravi', 'Present', '2026-09-04T05:49:00+05:30', '2026-09-04T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-04', 'W003', 'Selvam', 'Present', '2026-09-04T05:36:00+05:30', '2026-09-04T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-04', 'W004', 'Mani', 'Present', '2026-09-04T05:55:00+05:30', '2026-09-04T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-04', 'W005', 'Arun', 'Present', '2026-09-04T06:02:00+05:30', '2026-09-04T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-04', 'COW001', 18.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-04', 'COW002', 20.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-04', 'COW003', 16.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-04', 'COW004', 21.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-04', 'COW005', 17.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-04', 'COW006', 20.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-04', 'COW007', 19.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-04-AM', '2026-09-04', '2026-09-04T06:13:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 133.0, 92.8, 35.8, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 7 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-04-PM', '2026-09-04', '2026-09-04T17:09:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 118.1, 81.2, 30.3, 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-04-P1', '2026-09-04', '2026-09-04T08:28:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-04-P2', '2026-09-04', '2026-09-04T09:17:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-04', 'COW001', 2949, 8.4, 487, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-04', 'COW002', 3449, 9.3, 469, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-04', 'COW003', 3780, 8.6, 386, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-04', 'COW004', 3253, 9.2, 431, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-04', 'COW005', 3670, 9.9, 493, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-04', 'COW006', 2787, 9.1, 415, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-04', 'COW007', 3856, 8.7, 397, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-04', 'COW008', 3278, 9.2, 408, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-04', 'COW009', 2999, 10.5, 428, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-04', 'COW010', 3855, 9.5, 381, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-04', 30.2, 75.5, 738.6, 251.1, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-04T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-04T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-04T06:13:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 7 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-04T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-04T08:28:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-04T17:09:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-04T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-05', 'Saturday', '5 workers present. Morning and evening feeding recorded. Total milk 136.8 L. Water use 744.8 L. Pen 1 cleaning status: Delayed. 1 actionable alert(s) generated.', 5, 136.8, 744.8, 1)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-05', '2026-09-05T06:35:00+05:30', '2026-09-05T16:05:00+05:30', 136.8)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-05', 'W001', 'Kumar', 'Present', '2026-09-05T05:42:00+05:30', '2026-09-05T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-05', 'W002', 'Ravi', 'Present', '2026-09-05T05:49:00+05:30', '2026-09-05T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-05', 'W003', 'Selvam', 'Present', '2026-09-05T05:36:00+05:30', '2026-09-05T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-05', 'W004', 'Mani', 'Present', '2026-09-05T05:55:00+05:30', '2026-09-05T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-05', 'W005', 'Arun', 'Present', '2026-09-05T06:02:00+05:30', '2026-09-05T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-05', 'COW001', 18.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-05', 'COW002', 21.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-05', 'COW003', 16.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-05', 'COW004', 22.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-05', 'COW005', 18.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-05', 'COW006', 19.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-05', 'COW007', 19.6, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-05-AM', '2026-09-05', '2026-09-05T06:17:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 132.7, 95.3, 37.4, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 4 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-05-PM', '2026-09-05', '2026-09-05T16:57:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 117.7, 83.3, 33.5, 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-05-P1', '2026-09-05', '2026-09-05T09:35:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Delayed', 'Dung accumulation detected for more than 90 minutes before cleaning. Floor cleaned and bedding refreshed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-05-P2', '2026-09-05', '2026-09-05T09:05:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-05', 'COW001', 2866, 8.9, 491, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-05', 'COW002', 3460, 9.5, 464, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-05', 'COW003', 2730, 9.6, 435, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-05', 'COW004', 3843, 8.5, 490, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-05', 'COW005', 2762, 8.6, 446, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-05', 'COW006', 3595, 8.7, 389, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-05', 'COW007', 3896, 8.7, 446, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-05', 'COW008', 3517, 9.2, 445, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-05', 'COW009', 3381, 10.5, 399, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-05', 'COW010', 3652, 8.7, 422, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-05', 32.1, 78.2, 744.8, 250.4, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-05T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-05T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-05T06:17:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 4 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-05T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-05T09:35:00+05:30', 'CAM03', 'Cleaning', 'Dung accumulation detected for more than 90 minutes before cleaning. Floor cleaned and bedding refreshed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-05T16:57:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-05T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');
INSERT INTO farm_alerts (alert_id, date, type, severity, cattle_id, source, details, recommended_action)
VALUES ('ALT-2026-09-05-HYGIENE', '2026-09-05', 'Pen hygiene delay', 'Low', NULL, 'CCTV AI', 'Dung remained visible in Pen 1 beyond target cleaning window.', 'Assign worker to clean Pen 1 and verify completion.')
ON CONFLICT (alert_id) DO NOTHING;

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-06', 'Sunday', '5 workers present. Morning and evening feeding recorded. Total milk 132.5 L. Water use 778.0 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 132.5, 778.0, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-06', '2026-09-06T06:35:00+05:30', '2026-09-06T16:05:00+05:30', 132.5)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-06', 'W001', 'Kumar', 'Present', '2026-09-06T05:42:00+05:30', '2026-09-06T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-06', 'W002', 'Ravi', 'Present', '2026-09-06T05:49:00+05:30', '2026-09-06T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-06', 'W003', 'Selvam', 'Present', '2026-09-06T05:36:00+05:30', '2026-09-06T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-06', 'W004', 'Mani', 'Present', '2026-09-06T05:55:00+05:30', '2026-09-06T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-06', 'W005', 'Arun', 'Present', '2026-09-06T06:02:00+05:30', '2026-09-06T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-06', 'COW001', 19.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-06', 'COW002', 20.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-06', 'COW003', 17.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-06', 'COW004', 20.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-06', 'COW005', 17.6, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-06', 'COW006', 19.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-06', 'COW007', 18.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-06-AM', '2026-09-06', '2026-09-06T06:19:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 128.1, 95.4, 37.7, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 3 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-06-PM', '2026-09-06', '2026-09-06T17:06:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 118.1, 88.0, 34.0, 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-06-P1', '2026-09-06', '2026-09-06T08:27:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-06-P2', '2026-09-06', '2026-09-06T09:06:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-06', 'COW001', 3779, 9.5, 455, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-06', 'COW002', 3426, 10.5, 387, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-06', 'COW003', 3879, 8.8, 481, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-06', 'COW004', 3689, 8.5, 408, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-06', 'COW005', 2944, 9.0, 457, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-06', 'COW006', 3844, 9.4, 405, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-06', 'COW007', 3921, 8.2, 451, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-06', 'COW008', 3811, 8.2, 415, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-06', 'COW009', 2833, 10.6, 394, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-06', 'COW010', 3268, 9.9, 442, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-06', 31.7, 76.8, 778.0, 246.2, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-06T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-06T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-06T06:19:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 3 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-06T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-06T08:27:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-06T17:06:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-06T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-07', 'Monday', '4 workers present. Morning and evening feeding recorded. Total milk 137.1 L. Water use 764.3 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 4, 137.1, 764.3, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-07', '2026-09-07T06:35:00+05:30', '2026-09-07T16:05:00+05:30', 137.1)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-07', 'W001', 'Kumar', 'Present', '2026-09-07T05:42:00+05:30', '2026-09-07T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-07', 'W002', 'Ravi', 'Present', '2026-09-07T05:49:00+05:30', '2026-09-07T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-07', 'W003', 'Selvam', 'Present', '2026-09-07T05:36:00+05:30', '2026-09-07T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-07', 'W004', 'Mani', 'Present', '2026-09-07T05:55:00+05:30', '2026-09-07T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-07', 'W005', 'Arun', 'Absent', NULL, NULL, 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-07', 'COW001', 18.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-07', 'COW002', 21.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-07', 'COW003', 18.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-07', 'COW004', 20.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-07', 'COW005', 17.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-07', 'COW006', 20.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-07', 'COW007', 19.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-07-AM', '2026-09-07', '2026-09-07T06:10:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 132.5, 93.2, 34.6, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 3 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-07-PM', '2026-09-07', '2026-09-07T16:59:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 121.5, 84.2, 30.6, 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-07-P1', '2026-09-07', '2026-09-07T08:11:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-07-P2', '2026-09-07', '2026-09-07T09:09:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-07', 'COW001', 4013, 10.0, 486, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-07', 'COW002', 2981, 8.5, 470, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-07', 'COW003', 2897, 9.2, 396, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-07', 'COW004', 3944, 10.1, 424, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-07', 'COW005', 3587, 10.0, 404, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-07', 'COW006', 2872, 9.9, 420, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-07', 'COW007', 2704, 9.3, 398, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-07', 'COW008', 3935, 9.0, 473, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-07', 'COW009', 3869, 8.7, 454, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-07', 'COW010', 3207, 8.8, 383, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-07', 31.6, 77.8, 764.3, 254.0, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-07T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 4 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-07T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-07T06:10:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 3 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-07T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-07T08:11:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-07T16:59:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-07T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-08', 'Tuesday', '5 workers present. Morning and evening feeding recorded. Total milk 135.7 L. Water use 727.1 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 135.7, 727.1, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-08', '2026-09-08T06:35:00+05:30', '2026-09-08T16:05:00+05:30', 135.7)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-08', 'W001', 'Kumar', 'Present', '2026-09-08T05:42:00+05:30', '2026-09-08T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-08', 'W002', 'Ravi', 'Present', '2026-09-08T05:49:00+05:30', '2026-09-08T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-08', 'W003', 'Selvam', 'Present', '2026-09-08T05:36:00+05:30', '2026-09-08T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-08', 'W004', 'Mani', 'Present', '2026-09-08T05:55:00+05:30', '2026-09-08T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-08', 'W005', 'Arun', 'Present', '2026-09-08T06:02:00+05:30', '2026-09-08T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-08', 'COW001', 20.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-08', 'COW002', 20.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-08', 'COW003', 16.6, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-08', 'COW004', 21.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-08', 'COW005', 18.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-08', 'COW006', 19.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-08', 'COW007', 18.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-08-AM', '2026-09-08', '2026-09-08T06:21:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 127.2, 91.6, 36.7, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 7 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-08-PM', '2026-09-08', '2026-09-08T17:05:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 117.0, 79.2, 33.5, 'Evening feeding completed. Feed pushed toward manger after distribution. 1 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-08-P1', '2026-09-08', '2026-09-08T08:15:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-08-P2', '2026-09-08', '2026-09-08T09:18:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-08', 'COW001', 3006, 9.9, 375, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-08', 'COW002', 3945, 9.5, 461, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-08', 'COW003', 3688, 9.8, 418, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-08', 'COW004', 2747, 9.8, 414, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-08', 'COW005', 3089, 10.3, 461, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-08', 'COW006', 3070, 8.9, 424, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-08', 'COW007', 3213, 8.9, 390, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-08', 'COW008', 3238, 10.5, 456, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-08', 'COW009', 3913, 9.7, 411, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-08', 'COW010', 3417, 8.1, 409, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-08', 32.0, 75.6, 727.1, 244.2, 'Normal', 'Intermittent')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-08T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-08T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-08T06:21:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 7 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-08T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-08T08:15:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-08T17:05:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 1 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-08T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-09', 'Wednesday', '5 workers present. Morning and evening feeding recorded. Total milk 136.2 L. Water use 658.1 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 136.2, 658.1, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-09', '2026-09-09T06:35:00+05:30', '2026-09-09T16:05:00+05:30', 136.2)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-09', 'W001', 'Kumar', 'Present', '2026-09-09T05:42:00+05:30', '2026-09-09T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-09', 'W002', 'Ravi', 'Present', '2026-09-09T05:49:00+05:30', '2026-09-09T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-09', 'W003', 'Selvam', 'Present', '2026-09-09T05:36:00+05:30', '2026-09-09T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-09', 'W004', 'Mani', 'Present', '2026-09-09T05:55:00+05:30', '2026-09-09T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-09', 'W005', 'Arun', 'Present', '2026-09-09T06:02:00+05:30', '2026-09-09T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-09', 'COW001', 18.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-09', 'COW002', 20.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-09', 'COW003', 17.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-09', 'COW004', 21.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-09', 'COW005', 18.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-09', 'COW006', 20.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-09', 'COW007', 19.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-09-AM', '2026-09-09', '2026-09-09T06:15:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 129.5, 89.9, 35.8, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-09-PM', '2026-09-09', '2026-09-09T17:15:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 115.9, 83.3, 33.6, 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-09-P1', '2026-09-09', '2026-09-09T08:15:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-09-P2', '2026-09-09', '2026-09-09T09:21:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-09', 'COW001', 2992, 9.3, 476, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-09', 'COW002', 2751, 9.2, 450, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-09', 'COW003', 2922, 9.9, 434, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-09', 'COW004', 2991, 9.8, 375, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-09', 'COW005', 3701, 10.1, 387, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-09', 'COW006', 3245, 8.6, 489, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-09', 'COW007', 3375, 8.2, 404, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-09', 'COW008', 3837, 9.3, 471, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-09', 'COW009', 3584, 10.7, 446, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-09', 'COW010', 3980, 10.4, 448, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-09', 31.6, 72.9, 658.1, 245.4, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-09T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-09T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-09T06:15:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-09T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-09T08:15:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-09T17:15:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-09T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-10', 'Thursday', '5 workers present. Morning and evening feeding recorded. Total milk 133.3 L. Water use 672.3 L. Pen 1 cleaning status: Completed on time. 1 actionable alert(s) generated.', 5, 133.3, 672.3, 1)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-10', '2026-09-10T06:35:00+05:30', '2026-09-10T16:05:00+05:30', 133.3)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-10', 'W001', 'Kumar', 'Present', '2026-09-10T05:42:00+05:30', '2026-09-10T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-10', 'W002', 'Ravi', 'Present', '2026-09-10T05:49:00+05:30', '2026-09-10T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-10', 'W003', 'Selvam', 'Present', '2026-09-10T05:36:00+05:30', '2026-09-10T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-10', 'W004', 'Mani', 'Present', '2026-09-10T05:55:00+05:30', '2026-09-10T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-10', 'W005', 'Arun', 'Present', '2026-09-10T06:02:00+05:30', '2026-09-10T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-10', 'COW001', 19.6, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-10', 'COW002', 20.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-10', 'COW003', 17.6, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-10', 'COW004', 21.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-10', 'COW005', 17.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-10', 'COW006', 19.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-10', 'COW007', 18.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-10-AM', '2026-09-10', '2026-09-10T06:20:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 127.8, 95.2, 35.8, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 4 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-10-PM', '2026-09-10', '2026-09-10T17:13:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 120.7, 83.3, 31.0, 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-10-P1', '2026-09-10', '2026-09-10T08:30:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-10-P2', '2026-09-10', '2026-09-10T09:08:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-10', 'COW001', 2973, 9.9, 459, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-10', 'COW002', 2739, 9.2, 440, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-10', 'COW003', 3232, 8.6, 425, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-10', 'COW004', 3916, 9.6, 458, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-10', 'COW005', 6100, 7.2, 420, 'High')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-10', 'COW006', 2658, 9.0, 465, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-10', 'COW007', 3844, 10.6, 425, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-10', 'COW008', 3696, 9.5, 447, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-10', 'COW009', 2958, 8.7, 427, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-10', 'COW010', 2690, 9.0, 456, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-10', 31.6, 73.1, 672.3, 248.5, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-10T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-10T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-10T06:20:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 4 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-10T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-10T08:30:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-10T17:13:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-10T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');
INSERT INTO farm_alerts (alert_id, date, type, severity, cattle_id, source, details, recommended_action)
VALUES ('ALT-2026-09-10-ESTRUS-001', '2026-09-10', 'Estrus suspected', 'Medium', 'COW005', 'Activity collar + CAM03', 'Activity increased 78% above 7-day baseline; repeated mounting behaviour detected.', 'Physically verify heat signs and plan insemination window.')
ON CONFLICT (alert_id) DO NOTHING;

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-11', 'Friday', '5 workers present. Morning and evening feeding recorded. Total milk 132.3 L. Water use 773.9 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 132.3, 773.9, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-11', '2026-09-11T06:35:00+05:30', '2026-09-11T16:05:00+05:30', 132.3)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-11', 'W001', 'Kumar', 'Present', '2026-09-11T05:42:00+05:30', '2026-09-11T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-11', 'W002', 'Ravi', 'Present', '2026-09-11T05:49:00+05:30', '2026-09-11T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-11', 'W003', 'Selvam', 'Present', '2026-09-11T05:36:00+05:30', '2026-09-11T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-11', 'W004', 'Mani', 'Present', '2026-09-11T05:55:00+05:30', '2026-09-11T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-11', 'W005', 'Arun', 'Present', '2026-09-11T06:02:00+05:30', '2026-09-11T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-11', 'COW001', 18.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-11', 'COW002', 21.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-11', 'COW003', 16.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-11', 'COW004', 20.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-11', 'COW005', 17.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-11', 'COW006', 19.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-11', 'COW007', 18.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-11-AM', '2026-09-11', '2026-09-11T06:15:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 131.6, 95.3, 37.9, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 7 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-11-PM', '2026-09-11', '2026-09-11T17:02:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 114.2, 82.5, 32.3, 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-11-P1', '2026-09-11', '2026-09-11T08:12:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-11-P2', '2026-09-11', '2026-09-11T09:20:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-11', 'COW001', 3240, 10.3, 431, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-11', 'COW002', 3698, 8.2, 489, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-11', 'COW003', 2963, 8.3, 489, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-11', 'COW004', 2706, 8.2, 404, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-11', 'COW005', 3824, 9.7, 403, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-11', 'COW006', 3312, 8.4, 488, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-11', 'COW007', 3301, 8.8, 419, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-11', 'COW008', 3498, 10.6, 461, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-11', 'COW009', 3738, 8.5, 412, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-11', 'COW010', 3460, 10.5, 444, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-11', 32.4, 69.5, 773.9, 245.8, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-11T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-11T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-11T06:15:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 7 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-11T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-11T08:12:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-11T17:02:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-11T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-12', 'Saturday', '5 workers present. Morning and evening feeding recorded. Total milk 132.8 L. Water use 761.2 L. Pen 1 cleaning status: Delayed. 1 actionable alert(s) generated.', 5, 132.8, 761.2, 1)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-12', '2026-09-12T06:35:00+05:30', '2026-09-12T16:05:00+05:30', 132.8)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-12', 'W001', 'Kumar', 'Present', '2026-09-12T05:42:00+05:30', '2026-09-12T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-12', 'W002', 'Ravi', 'Present', '2026-09-12T05:49:00+05:30', '2026-09-12T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-12', 'W003', 'Selvam', 'Present', '2026-09-12T05:36:00+05:30', '2026-09-12T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-12', 'W004', 'Mani', 'Present', '2026-09-12T05:55:00+05:30', '2026-09-12T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-12', 'W005', 'Arun', 'Present', '2026-09-12T06:02:00+05:30', '2026-09-12T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-12', 'COW001', 18.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-12', 'COW002', 19.6, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-12', 'COW003', 18.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-12', 'COW004', 21.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-12', 'COW005', 17.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-12', 'COW006', 19.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-12', 'COW007', 17.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-12-AM', '2026-09-12', '2026-09-12T06:23:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 127.6, 93.4, 34.3, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-12-PM', '2026-09-12', '2026-09-12T17:09:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 121.5, 81.2, 32.8, 'Evening feeding completed. Feed pushed toward manger after distribution. 1 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-12-P1', '2026-09-12', '2026-09-12T09:35:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Delayed', 'Dung accumulation detected for more than 90 minutes before cleaning. Floor cleaned and bedding refreshed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-12-P2', '2026-09-12', '2026-09-12T09:21:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-12', 'COW001', 3801, 8.4, 490, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-12', 'COW002', 3539, 10.3, 459, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-12', 'COW003', 3259, 10.0, 490, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-12', 'COW004', 3028, 10.2, 439, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-12', 'COW005', 3326, 9.2, 462, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-12', 'COW006', 3025, 10.3, 474, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-12', 'COW007', 2771, 10.4, 404, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-12', 'COW008', 3300, 9.7, 420, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-12', 'COW009', 2690, 10.3, 396, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-12', 'COW010', 2946, 10.2, 415, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-12', 31.5, 68.0, 761.2, 249.1, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-12T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-12T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-12T06:23:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-12T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-12T09:35:00+05:30', 'CAM03', 'Cleaning', 'Dung accumulation detected for more than 90 minutes before cleaning. Floor cleaned and bedding refreshed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-12T17:09:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 1 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-12T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');
INSERT INTO farm_alerts (alert_id, date, type, severity, cattle_id, source, details, recommended_action)
VALUES ('ALT-2026-09-12-HYGIENE', '2026-09-12', 'Pen hygiene delay', 'Low', NULL, 'CCTV AI', 'Dung remained visible in Pen 1 beyond target cleaning window.', 'Assign worker to clean Pen 1 and verify completion.')
ON CONFLICT (alert_id) DO NOTHING;

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-13', 'Sunday', '5 workers present. Morning and evening feeding recorded. Total milk 129.6 L. Water use 698.0 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 129.6, 698.0, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-13', '2026-09-13T06:35:00+05:30', '2026-09-13T16:05:00+05:30', 129.6)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-13', 'W001', 'Kumar', 'Present', '2026-09-13T05:42:00+05:30', '2026-09-13T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-13', 'W002', 'Ravi', 'Present', '2026-09-13T05:49:00+05:30', '2026-09-13T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-13', 'W003', 'Selvam', 'Present', '2026-09-13T05:36:00+05:30', '2026-09-13T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-13', 'W004', 'Mani', 'Present', '2026-09-13T05:55:00+05:30', '2026-09-13T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-13', 'W005', 'Arun', 'Present', '2026-09-13T06:02:00+05:30', '2026-09-13T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-13', 'COW001', 19.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-13', 'COW002', 20.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-13', 'COW003', 15.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-13', 'COW004', 20.6, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-13', 'COW005', 17.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-13', 'COW006', 18.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-13', 'COW007', 18.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-13-AM', '2026-09-13', '2026-09-13T06:23:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 129.0, 91.6, 34.8, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 4 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-13-PM', '2026-09-13', '2026-09-13T17:05:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 120.5, 83.4, 33.0, 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-13-P1', '2026-09-13', '2026-09-13T08:25:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-13-P2', '2026-09-13', '2026-09-13T09:20:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-13', 'COW001', 4045, 9.5, 417, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-13', 'COW002', 3285, 8.9, 402, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-13', 'COW003', 3659, 8.9, 464, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-13', 'COW004', 3981, 9.9, 397, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-13', 'COW005', 3684, 8.8, 445, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-13', 'COW006', 3714, 9.7, 492, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-13', 'COW007', 3815, 8.9, 418, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-13', 'COW008', 3073, 9.9, 390, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-13', 'COW009', 2713, 8.2, 410, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-13', 'COW010', 3971, 9.8, 465, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-13', 31.0, 67.8, 698.0, 249.5, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-13T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-13T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-13T06:23:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 4 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-13T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-13T08:25:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-13T17:05:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-13T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-14', 'Monday', '4 workers present. Morning and evening feeding recorded. Total milk 130.3 L. Water use 707.0 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 4, 130.3, 707.0, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-14', '2026-09-14T06:35:00+05:30', '2026-09-14T16:05:00+05:30', 130.3)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-14', 'W001', 'Kumar', 'Present', '2026-09-14T05:42:00+05:30', '2026-09-14T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-14', 'W002', 'Ravi', 'Present', '2026-09-14T05:49:00+05:30', '2026-09-14T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-14', 'W003', 'Selvam', 'Present', '2026-09-14T05:36:00+05:30', '2026-09-14T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-14', 'W004', 'Mani', 'Present', '2026-09-14T05:55:00+05:30', '2026-09-14T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-14', 'W005', 'Arun', 'Absent', NULL, NULL, 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-14', 'COW001', 18.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-14', 'COW002', 20.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-14', 'COW003', 17.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-14', 'COW004', 20.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-14', 'COW005', 18.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-14', 'COW006', 19.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-14', 'COW007', 16.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-14-AM', '2026-09-14', '2026-09-14T06:10:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 129.2, 91.2, 35.8, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 4 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-14-PM', '2026-09-14', '2026-09-14T16:57:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 122.7, 81.3, 33.4, 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-14-P1', '2026-09-14', '2026-09-14T08:12:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-14-P2', '2026-09-14', '2026-09-14T09:12:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-14', 'COW001', 3484, 9.7, 468, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-14', 'COW002', 3182, 10.5, 410, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-14', 'COW003', 3473, 9.2, 443, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-14', 'COW004', 2734, 10.6, 386, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-14', 'COW005', 3717, 9.7, 406, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-14', 'COW006', 2763, 8.7, 441, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-14', 'COW007', 2869, 9.2, 457, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-14', 'COW008', 3307, 8.2, 409, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-14', 'COW009', 3045, 10.3, 383, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-14', 'COW010', 2976, 8.8, 469, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-14', 30.4, 66.8, 707.0, 251.9, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-14T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 4 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-14T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-14T06:10:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 4 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-14T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-14T08:12:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-14T16:57:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-14T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-15', 'Tuesday', '5 workers present. Morning and evening feeding recorded. Total milk 125.7 L. Water use 729.8 L. Pen 1 cleaning status: Completed on time. 1 actionable alert(s) generated.', 5, 125.7, 729.8, 1)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-15', '2026-09-15T06:35:00+05:30', '2026-09-15T16:05:00+05:30', 125.7)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-15', 'W001', 'Kumar', 'Present', '2026-09-15T05:42:00+05:30', '2026-09-15T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-15', 'W002', 'Ravi', 'Present', '2026-09-15T05:49:00+05:30', '2026-09-15T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-15', 'W003', 'Selvam', 'Present', '2026-09-15T05:36:00+05:30', '2026-09-15T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-15', 'W004', 'Mani', 'Present', '2026-09-15T05:55:00+05:30', '2026-09-15T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-15', 'W005', 'Arun', 'Present', '2026-09-15T06:02:00+05:30', '2026-09-15T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-15', 'COW001', 18.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-15', 'COW002', 20.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-15', 'COW003', 13.3, 6.2, 450000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-15', 'COW004', 20.6, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-15', 'COW005', 16.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-15', 'COW006', 18.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-15', 'COW007', 17.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-15-AM', '2026-09-15', '2026-09-15T06:18:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 127.8, 91.9, 36.6, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 5 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-15-PM', '2026-09-15', '2026-09-15T17:03:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 121.4, 79.6, 30.7, 'Evening feeding completed. Feed pushed toward manger after distribution. 1 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-15-P1', '2026-09-15', '2026-09-15T08:29:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-15-P2', '2026-09-15', '2026-09-15T09:23:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-15', 'COW001', 3895, 10.0, 447, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-15', 'COW002', 2686, 8.7, 455, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-15', 'COW003', 3854, 9.6, 377, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-15', 'COW004', 3720, 10.2, 444, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-15', 'COW005', 3718, 8.6, 437, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-15', 'COW006', 3269, 8.8, 494, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-15', 'COW007', 3260, 10.2, 491, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-15', 'COW008', 3308, 9.2, 413, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-15', 'COW009', 2796, 8.5, 424, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-15', 'COW010', 3343, 9.8, 423, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-15', 30.4, 65.6, 729.8, 249.2, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-15T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-15T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-15T06:18:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 5 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-15T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-15T08:29:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-15T17:03:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 1 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-15T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');
INSERT INTO farm_alerts (alert_id, date, type, severity, cattle_id, source, details, recommended_action)
VALUES ('ALT-2026-09-15-MAST-001', '2026-09-15', 'Mastitis risk', 'High', 'COW003', 'Inline mastitis sensor', 'Quarter conductivity increased 19% from cow baseline; milk yield dropped 2.7 L/day.', 'Inspect udder, perform confirmatory mastitis test and segregate milk if clinically abnormal.')
ON CONFLICT (alert_id) DO NOTHING;

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-16', 'Wednesday', '5 workers present. Morning and evening feeding recorded. Total milk 122.3 L. Water use 691.0 L. Pen 1 cleaning status: Completed on time. 1 actionable alert(s) generated.', 5, 122.3, 691.0, 1)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-16', '2026-09-16T06:35:00+05:30', '2026-09-16T16:05:00+05:30', 122.3)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-16', 'W001', 'Kumar', 'Present', '2026-09-16T05:42:00+05:30', '2026-09-16T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-16', 'W002', 'Ravi', 'Present', '2026-09-16T05:49:00+05:30', '2026-09-16T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-16', 'W003', 'Selvam', 'Present', '2026-09-16T05:36:00+05:30', '2026-09-16T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-16', 'W004', 'Mani', 'Present', '2026-09-16T05:55:00+05:30', '2026-09-16T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-16', 'W005', 'Arun', 'Present', '2026-09-16T06:02:00+05:30', '2026-09-16T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-16', 'COW001', 17.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-16', 'COW002', 18.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-16', 'COW003', 13.3, 6.2, 450000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-16', 'COW004', 20.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-16', 'COW005', 16.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-16', 'COW006', 18.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-16', 'COW007', 16.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-16-AM', '2026-09-16', '2026-09-16T06:21:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 124.3, 87.8, 35.0, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 3 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-16-PM', '2026-09-16', '2026-09-16T17:14:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 122.7, 82.6, 32.1, 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-16-P1', '2026-09-16', '2026-09-16T08:31:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-16-P2', '2026-09-16', '2026-09-16T09:17:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-16', 'COW001', 3883, 9.4, 378, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-16', 'COW002', 3532, 10.2, 460, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-16', 'COW003', 3085, 8.1, 423, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-16', 'COW004', 2964, 10.3, 388, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-16', 'COW005', 3975, 9.8, 393, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-16', 'COW006', 3955, 8.9, 459, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-16', 'COW007', 3231, 9.4, 431, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-16', 'COW008', 3289, 8.5, 397, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-16', 'COW009', 3489, 10.0, 391, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-16', 'COW010', 2747, 10.1, 477, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-16', 29.5, 64.0, 691.0, 247.0, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-16T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-16T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-16T06:21:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 3 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-16T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-16T08:31:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-16T17:14:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-16T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');
INSERT INTO farm_alerts (alert_id, date, type, severity, cattle_id, source, details, recommended_action)
VALUES ('ALT-2026-09-16-MAST-002', '2026-09-16', 'Mastitis follow-up', 'Medium', 'COW003', 'Inline mastitis sensor', 'Conductivity remains elevated but lower than previous day.', 'Continue monitoring and record quarter-level test result.')
ON CONFLICT (alert_id) DO NOTHING;

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-17', 'Thursday', '5 workers present. Morning and evening feeding recorded. Total milk 125.3 L. Water use 751.9 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 125.3, 751.9, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-17', '2026-09-17T06:35:00+05:30', '2026-09-17T16:05:00+05:30', 125.3)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-17', 'W001', 'Kumar', 'Present', '2026-09-17T05:42:00+05:30', '2026-09-17T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-17', 'W002', 'Ravi', 'Present', '2026-09-17T05:49:00+05:30', '2026-09-17T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-17', 'W003', 'Selvam', 'Present', '2026-09-17T05:36:00+05:30', '2026-09-17T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-17', 'W004', 'Mani', 'Present', '2026-09-17T05:55:00+05:30', '2026-09-17T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-17', 'W005', 'Arun', 'Present', '2026-09-17T06:02:00+05:30', '2026-09-17T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-17', 'COW001', 17.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-17', 'COW002', 19.6, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-17', 'COW003', 16.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-17', 'COW004', 20.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-17', 'COW005', 16.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-17', 'COW006', 17.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-17', 'COW007', 17.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-17-AM', '2026-09-17', '2026-09-17T06:14:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 126.4, 87.0, 36.9, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 7 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-17-PM', '2026-09-17', '2026-09-17T17:13:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 119.2, 84.9, 33.5, 'Evening feeding completed. Feed pushed toward manger after distribution. 1 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-17-P1', '2026-09-17', '2026-09-17T08:27:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-17-P2', '2026-09-17', '2026-09-17T09:15:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-17', 'COW001', 2711, 10.0, 459, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-17', 'COW002', 3785, 9.1, 454, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-17', 'COW003', 3799, 10.7, 434, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-17', 'COW004', 2701, 9.4, 445, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-17', 'COW005', 3867, 10.4, 427, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-17', 'COW006', 3386, 9.3, 461, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-17', 'COW007', 3223, 9.8, 393, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-17', 'COW008', 3307, 10.6, 415, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-17', 'COW009', 3619, 9.8, 477, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-17', 'COW010', 3843, 10.3, 420, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-17', 29.5, 65.5, 751.9, 245.6, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-17T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-17T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-17T06:14:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 7 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-17T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-17T08:27:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-17T17:13:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 1 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-17T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-18', 'Friday', '5 workers present. Morning and evening feeding recorded. Total milk 122.9 L. Water use 708.8 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 122.9, 708.8, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-18', '2026-09-18T06:35:00+05:30', '2026-09-18T16:05:00+05:30', 122.9)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-18', 'W001', 'Kumar', 'Present', '2026-09-18T05:42:00+05:30', '2026-09-18T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-18', 'W002', 'Ravi', 'Present', '2026-09-18T05:49:00+05:30', '2026-09-18T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-18', 'W003', 'Selvam', 'Present', '2026-09-18T05:36:00+05:30', '2026-09-18T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-18', 'W004', 'Mani', 'Present', '2026-09-18T05:55:00+05:30', '2026-09-18T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-18', 'W005', 'Arun', 'Present', '2026-09-18T06:02:00+05:30', '2026-09-18T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-18', 'COW001', 18.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-18', 'COW002', 19.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-18', 'COW003', 15.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-18', 'COW004', 19.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-18', 'COW005', 16.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-18', 'COW006', 17.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-18', 'COW007', 16.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-18-AM', '2026-09-18', '2026-09-18T06:14:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 131.9, 87.3, 34.3, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-18-PM', '2026-09-18', '2026-09-18T17:12:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 120.2, 81.6, 30.9, 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-18-P1', '2026-09-18', '2026-09-18T08:23:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-18-P2', '2026-09-18', '2026-09-18T09:03:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-18', 'COW001', 2991, 9.2, 456, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-18', 'COW002', 2902, 8.6, 448, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-18', 'COW003', 3185, 9.9, 434, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-18', 'COW004', 3466, 8.7, 451, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-18', 'COW005', 3293, 9.8, 482, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-18', 'COW006', 3301, 8.8, 440, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-18', 'COW007', 2753, 10.6, 493, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-18', 'COW008', 3068, 10.6, 457, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-18', 'COW009', 3289, 8.9, 494, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-18', 'COW010', 3844, 8.4, 420, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-18', 28.2, 67.7, 708.8, 252.1, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-18T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-18T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-18T06:14:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-18T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-18T08:23:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-18T17:12:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-18T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-19', 'Saturday', '4 workers present. Morning and evening feeding recorded. Total milk 128.7 L. Water use 686.3 L. Pen 1 cleaning status: Delayed. 1 actionable alert(s) generated.', 4, 128.7, 686.3, 1)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-19', '2026-09-19T06:35:00+05:30', '2026-09-19T16:05:00+05:30', 128.7)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-19', 'W001', 'Kumar', 'Present', '2026-09-19T05:42:00+05:30', '2026-09-19T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-19', 'W002', 'Ravi', 'Present', '2026-09-19T05:49:00+05:30', '2026-09-19T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-19', 'W003', 'Selvam', 'Present', '2026-09-19T05:36:00+05:30', '2026-09-19T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-19', 'W004', 'Mani', 'Absent', NULL, NULL, 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-19', 'W005', 'Arun', 'Present', '2026-09-19T06:02:00+05:30', '2026-09-19T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-19', 'COW001', 18.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-19', 'COW002', 19.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-19', 'COW003', 16.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-19', 'COW004', 21.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-19', 'COW005', 17.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-19', 'COW006', 17.6, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-19', 'COW007', 17.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-19-AM', '2026-09-19', '2026-09-19T06:14:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 126.7, 93.3, 34.1, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-19-PM', '2026-09-19', '2026-09-19T17:15:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 117.6, 79.1, 33.5, 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-19-P1', '2026-09-19', '2026-09-19T09:35:00+05:30', 'W005', 'CAM03', 'Pen 1', 'Delayed', 'Dung accumulation detected for more than 90 minutes before cleaning. Floor cleaned and bedding refreshed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-19-P2', '2026-09-19', '2026-09-19T09:01:00+05:30', 'W005', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-19', 'COW001', 3707, 10.1, 456, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-19', 'COW002', 2841, 8.4, 450, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-19', 'COW003', 2705, 10.2, 379, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-19', 'COW004', 3160, 8.4, 484, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-19', 'COW005', 3107, 9.2, 399, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-19', 'COW006', 3751, 10.4, 418, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-19', 'COW007', 3352, 8.8, 394, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-19', 'COW008', 3929, 10.6, 491, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-19', 'COW009', 3063, 10.4, 471, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-19', 'COW010', 3305, 8.3, 465, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-19', 27.9, 68.5, 686.3, 244.3, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-19T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 4 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-19T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-19T06:14:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-19T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-19T09:35:00+05:30', 'CAM03', 'Cleaning', 'Dung accumulation detected for more than 90 minutes before cleaning. Floor cleaned and bedding refreshed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-19T17:15:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-19T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');
INSERT INTO farm_alerts (alert_id, date, type, severity, cattle_id, source, details, recommended_action)
VALUES ('ALT-2026-09-19-HYGIENE', '2026-09-19', 'Pen hygiene delay', 'Low', NULL, 'CCTV AI', 'Dung remained visible in Pen 1 beyond target cleaning window.', 'Assign worker to clean Pen 1 and verify completion.')
ON CONFLICT (alert_id) DO NOTHING;

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-20', 'Sunday', '5 workers present. Morning and evening feeding recorded. Total milk 124.6 L. Water use 731.3 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 124.6, 731.3, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-20', '2026-09-20T06:35:00+05:30', '2026-09-20T16:05:00+05:30', 124.6)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-20', 'W001', 'Kumar', 'Present', '2026-09-20T05:42:00+05:30', '2026-09-20T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-20', 'W002', 'Ravi', 'Present', '2026-09-20T05:49:00+05:30', '2026-09-20T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-20', 'W003', 'Selvam', 'Present', '2026-09-20T05:36:00+05:30', '2026-09-20T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-20', 'W004', 'Mani', 'Present', '2026-09-20T05:55:00+05:30', '2026-09-20T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-20', 'W005', 'Arun', 'Present', '2026-09-20T06:02:00+05:30', '2026-09-20T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-20', 'COW001', 17.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-20', 'COW002', 19.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-20', 'COW003', 16.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-20', 'COW004', 19.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-20', 'COW005', 17.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-20', 'COW006', 18.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-20', 'COW007', 17.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-20-AM', '2026-09-20', '2026-09-20T06:12:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 132.7, 94.2, 35.5, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 6 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-20-PM', '2026-09-20', '2026-09-20T17:09:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 114.1, 83.8, 31.8, 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-20-P1', '2026-09-20', '2026-09-20T08:33:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-20-P2', '2026-09-20', '2026-09-20T09:21:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-20', 'COW001', 3556, 9.8, 430, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-20', 'COW002', 3631, 9.8, 389, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-20', 'COW003', 2713, 8.2, 494, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-20', 'COW004', 2812, 8.7, 439, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-20', 'COW005', 3194, 9.1, 488, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-20', 'COW006', 3625, 9.5, 445, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-20', 'COW007', 3667, 10.4, 453, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-20', 'COW008', 3817, 9.7, 487, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-20', 'COW009', 3041, 9.9, 401, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-20', 'COW010', 3272, 8.7, 418, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-20', 28.7, 71.3, 731.3, 246.8, 'Normal', 'Intermittent')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-20T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-20T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-20T06:12:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 6 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-20T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-20T08:33:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-20T17:09:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-20T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-21', 'Monday', '4 workers present. Morning and evening feeding recorded. Total milk 126.1 L. Water use 724.3 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 4, 126.1, 724.3, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-21', '2026-09-21T06:35:00+05:30', '2026-09-21T16:05:00+05:30', 126.1)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-21', 'W001', 'Kumar', 'Present', '2026-09-21T05:42:00+05:30', '2026-09-21T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-21', 'W002', 'Ravi', 'Present', '2026-09-21T05:49:00+05:30', '2026-09-21T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-21', 'W003', 'Selvam', 'Present', '2026-09-21T05:36:00+05:30', '2026-09-21T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-21', 'W004', 'Mani', 'Present', '2026-09-21T05:55:00+05:30', '2026-09-21T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-21', 'W005', 'Arun', 'Absent', NULL, NULL, 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-21', 'COW001', 17.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-21', 'COW002', 19.6, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-21', 'COW003', 17.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-21', 'COW004', 19.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-21', 'COW005', 16.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-21', 'COW006', 19.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-21', 'COW007', 17.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-21-AM', '2026-09-21', '2026-09-21T06:19:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 128.9, 95.8, 35.4, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 6 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-21-PM', '2026-09-21', '2026-09-21T17:08:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 116.5, 87.7, 33.8, 'Evening feeding completed. Feed pushed toward manger after distribution. 1 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-21-P1', '2026-09-21', '2026-09-21T08:12:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-21-P2', '2026-09-21', '2026-09-21T09:21:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-21', 'COW001', 3470, 10.2, 402, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-21', 'COW002', 3734, 10.2, 446, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-21', 'COW003', 3038, 10.7, 493, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-21', 'COW004', 3406, 10.2, 388, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-21', 'COW005', 3863, 8.4, 417, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-21', 'COW006', 3753, 9.6, 376, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-21', 'COW007', 3021, 8.4, 425, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-21', 'COW008', 2809, 8.3, 428, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-21', 'COW009', 3156, 9.6, 429, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-21', 'COW010', 2960, 9.7, 462, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-21', 27.1, 76.2, 724.3, 245.4, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-21T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 4 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-21T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-21T06:19:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 6 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-21T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-21T08:12:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-21T17:08:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 1 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-21T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-22', 'Tuesday', '5 workers present. Morning and evening feeding recorded. Total milk 125.4 L. Water use 691.9 L. Pen 1 cleaning status: Completed on time. 1 actionable alert(s) generated.', 5, 125.4, 691.9, 1)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-22', '2026-09-22T06:35:00+05:30', '2026-09-22T16:05:00+05:30', 125.4)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-22', 'W001', 'Kumar', 'Present', '2026-09-22T05:42:00+05:30', '2026-09-22T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-22', 'W002', 'Ravi', 'Present', '2026-09-22T05:49:00+05:30', '2026-09-22T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-22', 'W003', 'Selvam', 'Present', '2026-09-22T05:36:00+05:30', '2026-09-22T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-22', 'W004', 'Mani', 'Present', '2026-09-22T05:55:00+05:30', '2026-09-22T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-22', 'W005', 'Arun', 'Present', '2026-09-22T06:02:00+05:30', '2026-09-22T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-22', 'COW001', 18.6, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-22', 'COW002', 19.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-22', 'COW003', 15.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-22', 'COW004', 19.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-22', 'COW005', 17.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-22', 'COW006', 18.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-22', 'COW007', 17.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-22-AM', '2026-09-22', '2026-09-22T06:23:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 126.7, 92.8, 34.1, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 6 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-22-PM', '2026-09-22', '2026-09-22T17:13:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 121.6, 82.8, 30.4, 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-22-P1', '2026-09-22', '2026-09-22T08:24:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-22-P2', '2026-09-22', '2026-09-22T09:02:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-22', 'COW001', 3357, 9.2, 470, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-22', 'COW002', 5750, 9.8, 480, 'High')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-22', 'COW003', 3421, 10.4, 426, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-22', 'COW004', 3893, 9.2, 474, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-22', 'COW005', 3208, 10.0, 412, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-22', 'COW006', 3087, 8.8, 489, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-22', 'COW007', 3611, 9.3, 385, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-22', 'COW008', 2769, 9.2, 464, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-22', 'COW009', 3171, 8.4, 382, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-22', 'COW010', 3989, 9.6, 455, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-22', 27.1, 76.5, 691.9, 248.3, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-22T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-22T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-22T06:23:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 6 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-22T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-22T08:24:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-22T17:13:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-22T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');
INSERT INTO farm_alerts (alert_id, date, type, severity, cattle_id, source, details, recommended_action)
VALUES ('ALT-2026-09-22-ESTRUS-002', '2026-09-22', 'Estrus suspected', 'Medium', 'COW002', 'Activity collar + CAM03', 'Activity increased 64%; standing heat behaviour detected twice.', 'Verify estrus and record breeding decision.')
ON CONFLICT (alert_id) DO NOTHING;

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-23', 'Wednesday', '5 workers present. Morning and evening feeding recorded. Total milk 123.5 L. Water use 760.6 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 123.5, 760.6, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-23', '2026-09-23T06:35:00+05:30', '2026-09-23T16:05:00+05:30', 123.5)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-23', 'W001', 'Kumar', 'Present', '2026-09-23T05:42:00+05:30', '2026-09-23T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-23', 'W002', 'Ravi', 'Present', '2026-09-23T05:49:00+05:30', '2026-09-23T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-23', 'W003', 'Selvam', 'Present', '2026-09-23T05:36:00+05:30', '2026-09-23T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-23', 'W004', 'Mani', 'Present', '2026-09-23T05:55:00+05:30', '2026-09-23T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-23', 'W005', 'Arun', 'Present', '2026-09-23T06:02:00+05:30', '2026-09-23T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-23', 'COW001', 17.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-23', 'COW002', 19.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-23', 'COW003', 15.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-23', 'COW004', 19.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-23', 'COW005', 17.6, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-23', 'COW006', 15.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-23', 'COW007', 17.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-23-AM', '2026-09-23', '2026-09-23T06:15:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 131.9, 95.5, 35.7, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-23-PM', '2026-09-23', '2026-09-23T17:08:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 114.5, 81.6, 31.2, 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-23-P1', '2026-09-23', '2026-09-23T08:28:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-23-P2', '2026-09-23', '2026-09-23T09:16:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-23', 'COW001', 4014, 10.2, 448, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-23', 'COW002', 3549, 8.2, 486, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-23', 'COW003', 3811, 8.8, 396, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-23', 'COW004', 3633, 8.9, 415, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-23', 'COW005', 2658, 10.4, 442, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-23', 'COW006', 3211, 8.5, 450, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-23', 'COW007', 2692, 10.0, 400, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-23', 'COW008', 3237, 9.0, 419, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-23', 'COW009', 3660, 10.1, 443, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-23', 'COW010', 2768, 8.2, 393, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-23', 27.2, 79.0, 760.6, 246.4, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-23T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-23T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-23T06:15:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-23T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-23T08:28:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-23T17:08:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-23T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-24', 'Thursday', '5 workers present. Morning and evening feeding recorded. Total milk 124.2 L. Water use 692.7 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 124.2, 692.7, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-24', '2026-09-24T06:35:00+05:30', '2026-09-24T16:05:00+05:30', 124.2)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-24', 'W001', 'Kumar', 'Present', '2026-09-24T05:42:00+05:30', '2026-09-24T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-24', 'W002', 'Ravi', 'Present', '2026-09-24T05:49:00+05:30', '2026-09-24T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-24', 'W003', 'Selvam', 'Present', '2026-09-24T05:36:00+05:30', '2026-09-24T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-24', 'W004', 'Mani', 'Present', '2026-09-24T05:55:00+05:30', '2026-09-24T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-24', 'W005', 'Arun', 'Present', '2026-09-24T06:02:00+05:30', '2026-09-24T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-24', 'COW001', 17.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-24', 'COW002', 19.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-24', 'COW003', 16.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-24', 'COW004', 20.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-24', 'COW005', 17.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-24', 'COW006', 15.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-24', 'COW007', 17.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-24-AM', '2026-09-24', '2026-09-24T06:18:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 130.1, 89.4, 36.6, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 6 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-24-PM', '2026-09-24', '2026-09-24T16:58:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 119.5, 82.7, 30.9, 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-24-P1', '2026-09-24', '2026-09-24T08:13:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-24-P2', '2026-09-24', '2026-09-24T09:11:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-24', 'COW001', 2945, 8.5, 405, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-24', 'COW002', 3109, 8.1, 464, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-24', 'COW003', 2895, 9.1, 459, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-24', 'COW004', 3350, 10.3, 471, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-24', 'COW005', 2750, 10.3, 380, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-24', 'COW006', 2676, 10.5, 478, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-24', 'COW007', 3456, 9.6, 460, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-24', 'COW008', 3234, 8.4, 377, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-24', 'COW009', 3104, 10.2, 449, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-24', 'COW010', 3814, 10.5, 385, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-24', 27.2, 74.9, 692.7, 249.6, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-24T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-24T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-24T06:18:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 6 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-24T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-24T08:13:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-24T16:58:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-24T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-25', 'Friday', '4 workers present. Morning and evening feeding recorded. Total milk 130.1 L. Water use 687.0 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 4, 130.1, 687.0, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-25', '2026-09-25T06:35:00+05:30', '2026-09-25T16:05:00+05:30', 130.1)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-25', 'W001', 'Kumar', 'Present', '2026-09-25T05:42:00+05:30', '2026-09-25T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-25', 'W002', 'Ravi', 'Absent', NULL, NULL, 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-25', 'W003', 'Selvam', 'Present', '2026-09-25T05:36:00+05:30', '2026-09-25T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-25', 'W004', 'Mani', 'Present', '2026-09-25T05:55:00+05:30', '2026-09-25T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-25', 'W005', 'Arun', 'Present', '2026-09-25T06:02:00+05:30', '2026-09-25T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-25', 'COW001', 18.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-25', 'COW002', 19.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-25', 'COW003', 15.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-25', 'COW004', 21.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-25', 'COW005', 16.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-25', 'COW006', 19.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-25', 'COW007', 18.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-25-AM', '2026-09-25', '2026-09-25T06:22:00+05:30', 'W001', 'Feed alley', 'CAM05', 'Pen 1', 126.2, 92.3, 36.1, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 6 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-25-PM', '2026-09-25', '2026-09-25T17:00:00+05:30', 'W001', 'Feed alley', 'CAM05', 'Pen 1', 121.8, 85.7, 30.9, 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-25-P1', '2026-09-25', '2026-09-25T08:12:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-25-P2', '2026-09-25', '2026-09-25T09:16:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-25', 'COW001', 2892, 8.5, 466, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-25', 'COW002', 2755, 10.6, 450, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-25', 'COW003', 3299, 9.6, 444, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-25', 'COW004', 3603, 10.4, 452, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-25', 'COW005', 4031, 8.9, 491, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-25', 'COW006', 3092, 9.2, 431, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-25', 'COW007', 3533, 10.2, 445, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-25', 'COW008', 3142, 8.3, 430, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-25', 'COW009', 2702, 9.1, 409, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-25', 'COW010', 3552, 10.6, 385, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-25', 26.4, 75.6, 687.0, 248.0, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-25T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 4 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-25T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-25T06:22:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 6 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-25T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-25T08:12:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-25T17:00:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-25T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-26', 'Saturday', '5 workers present. Morning and evening feeding recorded. Total milk 127.7 L. Water use 676.6 L. Pen 1 cleaning status: Delayed. 1 actionable alert(s) generated.', 5, 127.7, 676.6, 1)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-26', '2026-09-26T06:35:00+05:30', '2026-09-26T16:05:00+05:30', 127.7)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-26', 'W001', 'Kumar', 'Present', '2026-09-26T05:42:00+05:30', '2026-09-26T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-26', 'W002', 'Ravi', 'Present', '2026-09-26T05:49:00+05:30', '2026-09-26T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-26', 'W003', 'Selvam', 'Present', '2026-09-26T05:36:00+05:30', '2026-09-26T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-26', 'W004', 'Mani', 'Present', '2026-09-26T05:55:00+05:30', '2026-09-26T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-26', 'W005', 'Arun', 'Present', '2026-09-26T06:02:00+05:30', '2026-09-26T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-26', 'COW001', 18.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-26', 'COW002', 20.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-26', 'COW003', 15.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-26', 'COW004', 19.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-26', 'COW005', 16.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-26', 'COW006', 19.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-26', 'COW007', 17.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-26-AM', '2026-09-26', '2026-09-26T06:18:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 127.5, 92.2, 37.8, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-26-PM', '2026-09-26', '2026-09-26T17:13:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 122.1, 83.0, 33.2, 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-26-P1', '2026-09-26', '2026-09-26T09:35:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Delayed', 'Dung accumulation detected for more than 90 minutes before cleaning. Floor cleaned and bedding refreshed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-26-P2', '2026-09-26', '2026-09-26T09:06:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-26', 'COW001', 2996, 9.2, 427, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-26', 'COW002', 3381, 8.5, 419, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-26', 'COW003', 3046, 9.2, 415, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-26', 'COW004', 3487, 10.2, 452, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-26', 'COW005', 2742, 8.3, 456, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-26', 'COW006', 3047, 10.0, 453, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-26', 'COW007', 3918, 10.4, 415, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-26', 'COW008', 3465, 8.5, 416, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-26', 'COW009', 4004, 9.9, 422, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-26', 'COW010', 3483, 10.5, 412, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-26', 27.4, 77.4, 676.6, 249.6, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-26T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-26T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-26T06:18:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-26T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-26T09:35:00+05:30', 'CAM03', 'Cleaning', 'Dung accumulation detected for more than 90 minutes before cleaning. Floor cleaned and bedding refreshed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-26T17:13:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-26T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');
INSERT INTO farm_alerts (alert_id, date, type, severity, cattle_id, source, details, recommended_action)
VALUES ('ALT-2026-09-26-HYGIENE', '2026-09-26', 'Pen hygiene delay', 'Low', NULL, 'CCTV AI', 'Dung remained visible in Pen 1 beyond target cleaning window.', 'Assign worker to clean Pen 1 and verify completion.')
ON CONFLICT (alert_id) DO NOTHING;

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-27', 'Sunday', '5 workers present. Morning and evening feeding recorded. Total milk 130.0 L. Water use 760.6 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 130.0, 760.6, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-27', '2026-09-27T06:35:00+05:30', '2026-09-27T16:05:00+05:30', 130.0)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-27', 'W001', 'Kumar', 'Present', '2026-09-27T05:42:00+05:30', '2026-09-27T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-27', 'W002', 'Ravi', 'Present', '2026-09-27T05:49:00+05:30', '2026-09-27T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-27', 'W003', 'Selvam', 'Present', '2026-09-27T05:36:00+05:30', '2026-09-27T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-27', 'W004', 'Mani', 'Present', '2026-09-27T05:55:00+05:30', '2026-09-27T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-27', 'W005', 'Arun', 'Present', '2026-09-27T06:02:00+05:30', '2026-09-27T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-27', 'COW001', 18.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-27', 'COW002', 20.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-27', 'COW003', 16.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-27', 'COW004', 20.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-27', 'COW005', 18.6, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-27', 'COW006', 19.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-27', 'COW007', 17.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-27-AM', '2026-09-27', '2026-09-27T06:15:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 131.3, 93.0, 37.3, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-27-PM', '2026-09-27', '2026-09-27T17:07:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 123.0, 87.2, 30.4, 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-27-P1', '2026-09-27', '2026-09-27T08:23:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-27-P2', '2026-09-27', '2026-09-27T09:16:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-27', 'COW001', 2791, 10.1, 475, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-27', 'COW002', 3887, 8.2, 415, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-27', 'COW003', 3722, 8.4, 420, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-27', 'COW004', 2877, 10.3, 467, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-27', 'COW005', 3782, 8.5, 427, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-27', 'COW006', 3225, 9.9, 403, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-27', 'COW007', 3271, 8.8, 464, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-27', 'COW008', 3278, 9.5, 412, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-27', 'COW009', 3782, 9.3, 475, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-27', 'COW010', 3164, 10.6, 493, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-27', 26.7, 73.6, 760.6, 254.3, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-27T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-27T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-27T06:15:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 8 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-27T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-27T08:23:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-27T17:07:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-27T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-28', 'Monday', '4 workers present. Morning and evening feeding recorded. Total milk 132.3 L. Water use 719.2 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 4, 132.3, 719.2, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-28', '2026-09-28T06:35:00+05:30', '2026-09-28T16:05:00+05:30', 132.3)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-28', 'W001', 'Kumar', 'Present', '2026-09-28T05:42:00+05:30', '2026-09-28T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-28', 'W002', 'Ravi', 'Present', '2026-09-28T05:49:00+05:30', '2026-09-28T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-28', 'W003', 'Selvam', 'Present', '2026-09-28T05:36:00+05:30', '2026-09-28T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-28', 'W004', 'Mani', 'Present', '2026-09-28T05:55:00+05:30', '2026-09-28T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-28', 'W005', 'Arun', 'Absent', NULL, NULL, 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-28', 'COW001', 18.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-28', 'COW002', 20.2, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-28', 'COW003', 18.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-28', 'COW004', 21.7, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-28', 'COW005', 17.8, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-28', 'COW006', 18.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-28', 'COW007', 17.3, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-28-AM', '2026-09-28', '2026-09-28T06:16:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 131.0, 91.5, 35.7, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 4 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-28-PM', '2026-09-28', '2026-09-28T17:06:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 121.4, 86.2, 30.6, 'Evening feeding completed. Feed pushed toward manger after distribution. 1 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-28-P1', '2026-09-28', '2026-09-28T08:11:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-28-P2', '2026-09-28', '2026-09-28T09:20:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-28', 'COW001', 3813, 8.3, 484, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-28', 'COW002', 3793, 10.4, 486, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-28', 'COW003', 3230, 9.1, 419, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-28', 'COW004', 3190, 8.3, 401, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-28', 'COW005', 3096, 8.4, 460, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-28', 'COW006', 3119, 8.5, 379, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-28', 'COW007', 3934, 9.3, 474, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-28', 'COW008', 3712, 9.3, 448, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-28', 'COW009', 3918, 8.1, 400, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-28', 'COW010', 2859, 10.5, 448, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-28', 27.0, 74.2, 719.2, 252.4, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-28T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 4 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-28T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-28T06:16:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 4 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-28T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-28T08:11:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-28T17:06:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 1 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-28T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-29', 'Tuesday', '5 workers present. Morning and evening feeding recorded. Total milk 133.2 L. Water use 738.5 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 133.2, 738.5, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-29', '2026-09-29T06:35:00+05:30', '2026-09-29T16:05:00+05:30', 133.2)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-29', 'W001', 'Kumar', 'Present', '2026-09-29T05:42:00+05:30', '2026-09-29T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-29', 'W002', 'Ravi', 'Present', '2026-09-29T05:49:00+05:30', '2026-09-29T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-29', 'W003', 'Selvam', 'Present', '2026-09-29T05:36:00+05:30', '2026-09-29T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-29', 'W004', 'Mani', 'Present', '2026-09-29T05:55:00+05:30', '2026-09-29T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-29', 'W005', 'Arun', 'Present', '2026-09-29T06:02:00+05:30', '2026-09-29T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-29', 'COW001', 19.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-29', 'COW002', 20.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-29', 'COW003', 17.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-29', 'COW004', 21.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-29', 'COW005', 17.5, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-29', 'COW006', 18.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-29', 'COW007', 18.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-29-AM', '2026-09-29', '2026-09-29T06:15:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 131.0, 89.1, 34.5, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 4 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-29-PM', '2026-09-29', '2026-09-29T17:00:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 117.8, 86.1, 31.8, 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-29-P1', '2026-09-29', '2026-09-29T08:25:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-29-P2', '2026-09-29', '2026-09-29T09:19:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-29', 'COW001', 3382, 9.0, 489, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-29', 'COW002', 3411, 10.1, 435, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-29', 'COW003', 2678, 10.4, 380, 'Low')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-29', 'COW004', 3191, 9.1, 464, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-29', 'COW005', 3149, 8.3, 403, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-29', 'COW006', 3569, 8.4, 444, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-29', 'COW007', 3709, 8.4, 417, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-29', 'COW008', 3123, 9.8, 474, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-29', 'COW009', 3608, 10.7, 432, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-29', 'COW010', 2905, 8.5, 460, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-29', 28.0, 70.7, 738.5, 248.8, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-29T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-29T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-29T06:15:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 4 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-29T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-29T08:25:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-29T17:00:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 0 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-29T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');

INSERT INTO daily_summaries (date, weekday, summary_text, total_workers_present, total_milk_litres, total_water_litres, actionable_alerts_count)
VALUES ('2026-09-30', 'Wednesday', '5 workers present. Morning and evening feeding recorded. Total milk 133.5 L. Water use 705.0 L. Pen 1 cleaning status: Completed on time. 0 actionable alert(s) generated.', 5, 133.5, 705.0, 0)
ON CONFLICT (date) DO UPDATE SET summary_text = EXCLUDED.summary_text;
INSERT INTO daily_milking_totals (date, morning_session_start, evening_session_start, total_milk_litres)
VALUES ('2026-09-30', '2026-09-30T06:35:00+05:30', '2026-09-30T16:05:00+05:30', 133.5)
ON CONFLICT (date) DO UPDATE SET total_milk_litres = EXCLUDED.total_milk_litres;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-30', 'W001', 'Kumar', 'Present', '2026-09-30T05:42:00+05:30', '2026-09-30T17:48:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-30', 'W002', 'Ravi', 'Present', '2026-09-30T05:49:00+05:30', '2026-09-30T17:20:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-30', 'W003', 'Selvam', 'Present', '2026-09-30T05:36:00+05:30', '2026-09-30T16:45:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-30', 'W004', 'Mani', 'Present', '2026-09-30T05:55:00+05:30', '2026-09-30T17:10:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO worker_attendance (date, worker_id, worker_name, status, first_seen, last_seen, detected_by)
VALUES ('2026-09-30', 'W005', 'Arun', 'Present', '2026-09-30T06:02:00+05:30', '2026-09-30T17:30:00+05:30', 'CAM01')
ON CONFLICT (date, worker_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-30', 'COW001', 18.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-30', 'COW002', 21.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-30', 'COW003', 16.9, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-30', 'COW004', 22.4, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-30', 'COW005', 17.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-30', 'COW006', 20.0, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_milk_yields (date, cattle_id, yield_litres, conductivity_ms, somatic_cell_count)
VALUES ('2026-09-30', 'COW007', 18.1, 5.2, 140000)
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-30-AM', '2026-09-30', '2026-09-30T06:16:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 126.6, 87.4, 34.8, 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 3 minutes.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO feeding_events (event_id, date, time, worker_id, location, camera_id, cattle_group, tmr_kg, green_fodder_kg, concentrate_kg, camera_observation)
VALUES ('FEED-2026-09-30-PM', '2026-09-30', '2026-09-30T16:58:00+05:30', 'W002', 'Feed alley', 'CAM05', 'Pen 1', 116.8, 81.8, 31.6, 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-30-P1', '2026-09-30', '2026-09-30T08:25:00+05:30', 'W004', 'CAM03', 'Pen 1', 'Completed on time', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cleaning_events (event_id, date, time, worker_id, camera_id, area, status, camera_observation)
VALUES ('CLEAN-2026-09-30-P2', '2026-09-30', '2026-09-30T09:08:00+05:30', 'W004', 'CAM04', 'Pen 2', 'Completed', 'Pen 2 floor cleaned. No major wet bedding zone detected after cleaning.')
ON CONFLICT (event_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-30', 'COW001', 3265, 10.6, 415, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-30', 'COW002', 2911, 9.9, 419, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-30', 'COW003', 3766, 8.8, 384, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-30', 'COW004', 3244, 9.2, 494, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-30', 'COW005', 2902, 8.9, 387, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-30', 'COW006', 3109, 8.9, 428, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-30', 'COW007', 3654, 8.5, 428, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-30', 'COW008', 3275, 10.0, 484, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-30', 'COW009', 3510, 9.2, 451, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO cattle_activity (date, cattle_id, steps, rest_hours, rumination_minutes, activity_status)
VALUES ('2026-09-30', 'COW010', 3758, 8.2, 455, 'Normal')
ON CONFLICT (date, cattle_id) DO NOTHING;
INSERT INTO environment_iot (date, average_temperature_c, average_humidity_percent, water_consumption_litres, feed_distributed_kg, power_status, network_status)
VALUES ('2026-09-30', 28.8, 70.2, 705.0, 243.4, 'Normal', 'Online')
ON CONFLICT (date) DO NOTHING;
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-30T05:34:00+05:30', 'CAM01', 'Farm activity start', 'First farm worker activity detected near main gate. Expected workforce today: 5 workers.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-30T05:58:00+05:30', 'CAM03', 'Cattle movement', 'Lactating group standing and moving toward feed alley before morning feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-30T06:16:00+05:30', 'CAM05', 'Feeding', 'Worker entered feed alley and distributed morning ration to Pen 1 cattle. All 7 lactating cows approached feed line within 3 minutes.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-30T06:42:00+05:30', 'CAM02', 'Milking', 'Morning milking session in progress. Cows moved through parlour in normal sequence.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-30T08:25:00+05:30', 'CAM03', 'Cleaning', 'Dung scraping and floor cleaning completed. Bedding condition visually acceptable after cleaning.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-30T16:58:00+05:30', 'CAM05', 'Feeding', 'Evening feeding completed. Feed pushed toward manger after distribution. 2 cows initially delayed before reaching feed.');
INSERT INTO cctv_camera_events (time, camera_id, event_type, event_description)
VALUES ('2026-09-30T17:45:00+05:30', 'CAM01', 'Farm activity closing', 'Most workers leaving farm. No unauthorized entry detected during closing window.');
