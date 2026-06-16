-- visit_timeline.csv 복원 뷰: 스타 스키마를 조인해 원본 형태로 재구성
CREATE OR REPLACE VIEW v_visit_timeline AS
SELECT
    v.patient_no                                    AS "환자번호",
    p.name                                          AS "환자명",
    v.visit_date                                    AS "내원일",
    v.receipt_no                                    AS "접수번호",
    v.receipt_type                                  AS "접수구분",
    v.charting                                      AS "증상·차팅",
    (SELECT string_agg(d.code || ' ' || d.name, ' / ' ORDER BY d.code)
       FROM visit_diagnosis vd
       JOIN diagnosis d ON d.code = vd.diagnosis_code
      WHERE vd.visit_id = v.id)                     AS "진단목록",
    (SELECT string_agg(rx.name, ', ' ORDER BY rx.name)
       FROM visit_prescription vp
       JOIN prescription rx ON rx.id = vp.prescription_id
      WHERE vp.visit_id = v.id)                     AS "처방목록",
    v.dx_count                                      AS "진단수",
    v.rx_count                                      AS "처방수"
FROM visit v
JOIN patient p ON p.patient_no = v.patient_no
ORDER BY v.id;
