SELECT event_id, event_level, vendor_name, model_name, setting_value,
       enable, serial
FROM ref.ref_event_op_setting_value where event_id in (25,26,27)

(25, 'Warning', '*', '*', ['80%', 'CPU WARNING Threshold'], True, '*')
(26, 'Warning', '*', '*', ['70%', 'MEMORY WARNING Threshold'], True, '*')
(27, 'Warning', '*', '*', ['70%', 'DISK WARNING Threshold'], True, '*')