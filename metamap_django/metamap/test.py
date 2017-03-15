import re
sql = '''
select distinct a.user_id,reflect("java.net.URLDecoder","decode",a.subclass_name) as name, a.plan_amount, a.current_amount, b.count0, a.plan_status, substr(a.create_time,1,19), substr(a.end_time,1,19), (case when a.plan_status=1 then null else substr(a.update_time,1,19) end) quit_time, d.user_real_name, d.user_mobile, c.gender, (case when c.birthday=-2 then null else 2016-substr(c.birthday,1,4) end), c.channel, c.province, c.city, substr(c.reg_time,1,19) create_time, substr(c.invest1st_time,1,19) invest1st_time, e.premium_final, e.premium_regular,g.invcount, g.suminv, g.redcount, g.sumred, g.regucount, g.sumregu, f.maxregular, h.maxnum, i.rfm, j.activity_tag_1, j.activity_tag_2, j.activity_tag_3 from (select * from jlc.user_plan_info where to_date(create_time)>='2016-10-12') a left join (select plan_id, count(plan_id) as count0 from jlc.user_plan_record group by plan_id) b on a.id=b.plan_id left join dim_jlc.dim_user_info c on a.user_id=c.userid left join jlc.user_info d on a.user_id=d.user_id left join (select userid, premium_final,premium_regular from fact_jlc.premium_record where create_date='20161121') e on a.user_id=e.userid left join (select userid, max(premium_regular) maxregular from fact_jlc.premium_record group by userid) f on a.user_id=f.userid left join (select userid, sum(investcount) as invcount, sum(investamount) as suminv, sum(redeemcount) as redcount, sum(redeemamount) as sumred, sum(regularcount) as regucount, sum(regularamount) as sumregu from dim_jlc.topic_user group by userid) g on a.user_id=g.userid left join (select userid, max(num) maxnum from fact_jlc.regular_info group by userid) h on a.user_id=h.userid left join dim_jlc.dim_user_portrait i on a.user_id=i.userid left join app_jlc.user_activity_tag j on a.user_id=j.userid
'''
print('pre %s' % sql)
matchObj = re.match(r'.*,(reflect\(.*\)).*,.*', sql, re.I | re.S)
if matchObj:
    sql = sql.replace(matchObj.group(1), '-999')


print(sql)