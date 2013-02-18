_href_pf_prog=None
def friendList(href_pfs):
	"""friendList({'<a href="..?id=1">name1</a>','<a href="..?id=3">name2</a>'}) 
	--> return {id1:name1,id2:name2} if success,return None if error"""
	if href_pfs is None:
		return None
	elif isinstance(href_pfs,str):
		href_pfs={href_pfs}
	global _href_pf_prog
	if _href_pf_prog is None:
		import re
		_href_pf_prog=re.compile(r'id=(\d+)">([^<]*?)</a>')

	name=dict()
	for href_pf in href_pfs:
		m=_href_pf_prog.search(href_pf)
		if m is None:
			return None
		name[m.group(1)]=m.group(2)
	return name

_statprog=None
def status(stats):
	"""return {statusId:dict_of_details,statusId2:dict2} if success, return None if error"""
	if stats is None:
		return None
	elif isinstance(stats,str):
		stats={stats}
	global _statprog
	if _statprog is None:
		import re
		_statprog=re.compile(r'<li[^>]+id="status-(?P<id>\d+)">.+?<h3>\s*(?P<content>.+?)</h3>\s*?(?:<div class="content">\s*<div[^>]+>(?P<orig>.*?)</div>\s*</div>)?\s*<div class="details">.+?<span class="duration">(?P<timestamp>[^<]+?)</span>',re.DOTALL)

	res=dict()
	for stat in stats:
		m=_statprog.search(stat)
		if m is None:
			print('status parse error.stat={}'.format(stat))
			continue
		else:
			tmpStat=dict()
			status_id=m.group('id')
			tmpStat['renrenId1'],tmpStat['cur_name'],tmpStat['cur_content']=split_owner(_drop_status_urls(m.group('content')))
			tmpStat['orig_owner'],tmpStat['orig_name'],tmpStat['orig_content']=split_owner(_drop_status_urls(m.group('orig')))
			tmpStat['timestamp']=m.group('timestamp').strip()
			res[status_id]=tmpStat
	return res 

_pf_prog=None
def profile_detail(content):
	"""keys in record: 
		edu_college/edu_senior/edu_junior/edu_primary,
		birth_year/birth_month/birth_day,
		gender,hometown"""
	if content is None:
		return None
	global _pf_prog
	if _pf_prog is None:
		import re
		_pf_prog=re.compile(r'<dt>([^:：]+)[:：]?\s*</dt>[^<]*<dd>(.*?)</dd>',re.DOTALL)
	content=_drop_pf_extra(''.join(content),' ')
	#orig tag/value saved in orig_pf
	orig_pf=dict()
	for m in _pf_prog.finditer(content):
		if m is None:
			return None
		orig_pf[m.group(1).strip(' ')]=m.group(2)
	#useful info saved in pf
	pf=dict()
	pf['edu_college']=_split_high_edu(orig_pf.get('大学',None))
	pf['edu_senior']=_split_low_edu(orig_pf.get('高中',None))
	pf['edu_junior']=_split_low_edu(orig_pf.get('初中',None))
	pf['edu_primary']=_split_low_edu(orig_pf.get('小学',None))
	pf['hometown']=_drop_pf_extra(orig_pf.get('家乡',''),r' ')
	pf['gender']=_get_gender(orig_pf.get('性别',None))
	pf.update(_get_birth(orig_pf.get('生日',None)))
	return pf

_pf_miniprog=None
def profile_mini(content):
	if content is None:
		return None
	global _pf_miniprog
	if _pf_miniprog is None:
		import re
		_pf_miniprog=re.compile(r'<li\sclass="(\w+?)">(.*?)</li>',re.DOTALL)
	content=_drop_pf_extra(''.join(content),' ')
	orig_pf=dict()
	for m in _pf_miniprog.finditer(content):
		orig_pf[m.group(1)]=m.group(2)
	mini_pf=dict()
	mini_pf['hometown']=_drop_pf_extra(orig_pf.get('hometown',''))[2:].strip(' ')
	mini_pf.update(_get_birth(orig_pf.get('birthday',None)))
	if 'birthday' in orig_pf:
		mini_pf['gender']=_get_gender(orig_pf.get('birthday',None))
	else:
		mini_pf['gender']=_get_gender(orig_pf.get('gender',None))
	edu_now=_drop_pf_extra(orig_pf.get('school',''))
	if edu_now.find('就读于') > -1:
		mini_pf['edu_now']=edu_now[3:].strip(' ')
	else:
		mini_pf['edu_now']=edu_now[1:-2].strip(' ')
	return mini_pf

#-----------------profile------------------
#birth and gender
_birthprog=None
def _get_birth(content):
	if content is None:
		return {'birth_year':None,'birth_month':None,'birth_day':None}
	global _birthprog
	if _birthprog is None:
		import re
		_birthprog=re.compile(r'(?:(\d+)[年后-])?(\d+)[月-](\d+)[日]?')
	m=_birthprog.search(_drop_pf_extra(content,r''))
	if m is None:
		return {'birth_year':None,'birth_month':None,'birth_day':None}
	return {'birth_year':m.group(1),'birth_month':m.group(2),'birth_day':m.group(3)}
def _get_gender(content):
	if content is None:
		return None
	if content.find('男')>-1:
		return 'm'
	elif content.find('女')>-1:
		return 'f'
	else:
		return None

#edu info
_edu_highprog=None
def _split_high_edu(content):
	if content is None:
		return None
	global _edu_highprog
	if _edu_highprog is None:
		import re
		_edu_highprog=re.compile(r'([^-<]+)-\s*(\d+)\s*年\s*(?:-([^-<]+))?<br>')
	schools=set()
	for m in _edu_highprog.finditer(_drop_pf_extra(content)):
		school=[]
		for x in m.group(1,2,3):
			if x is not None and x.strip(' ') != '':
				school.append(x.strip(' '))
		schools.add(tuple(school))
	return schools

_edu_lowprog=None
def _split_low_edu(content):
	if content is None:
		return None
	global _edu_lowprog
	if _edu_lowprog is None:
		import re
		_edu_lowprog=re.compile(r'([^-<]+)(?:-\s*(\d+)\s*年)?')
	schools=set()
	for m in _edu_lowprog.finditer(_drop_pf_extra(content)):
		school=[]
		for x in m.group(1,2):
			if x is not None and x.strip(' ') != '':
				school.append(x.strip(' '))
		schools.add(tuple(school))
	return schools

#drop extra
def _drop_pf_extra(content,target=r' '):
	return _sub_space(_drop_span((_drop_link(content))),target)

_linkprog=None
def _drop_link(content):
	if content is None:
		return None
	global _linkprog
	if _linkprog is None:
		import re
		_linkprog=re.compile(r'<a\s[^>]+?>([^<]*?)</a>')
	return _linkprog.sub(r'\1',content)

_spanprog=None
def _drop_span(content):
	if content is None:
		return None
	global _spanprog
	if _spanprog is None:
		import re
		_spanprog=re.compile(r'<span[^>]*>([^<]*?)</span>')
	return _spanprog.sub(r'\1',content)

_spaceprog=None
_space_likeprog=None
def _sub_space(content,target=r''):
	if not isinstance(content,str):
		return None
	global _spaceprog
	global _space_likeprog
	if _spaceprog is None:
		import re
		_space_likeprog=re.compile(r'(?:\\n)|(?:\\t)|(?:\\u3000)|(?:\u3000)|(?:&nbsp;)')
		_spaceprog=re.compile(r'\s+')
	return _spaceprog.sub(target,_space_likeprog.sub(target,content)).strip(' ')

#-----------------status------------------

def _drop_status_urls(content):
	if content is None:
		return None
	else:
		return _sub_space(drop_rrurl(drop_img(drop_pf(drop_pubpf(drop_at(content))))),r' ')

_pfprog=None
def drop_pf(content):
	if content is None:
		return None
	global _pfprog
	if _pfprog is None:
		import re
		_pfprog=re.compile(r'<a\W[^>]+?http://www.renren.com/profile.do\?id=(\d+)[^>]+>(.*?)</a>',re.DOTALL)
	return _pfprog.sub(r'(\1,\2)',content)

_pubpfprog=None
def drop_pubpf(content):
	if content is None:
		return None
	global _pubpfprog
	if _pubpfprog is None:
		import re
		_pubpfprog=re.compile(r'<a\W[^>]+?http://page.renren.com/(\d+)[^>]+>(.*?)</a>',re.DOTALL)
	return _pubpfprog.sub(r'(\1,\2)',str(content))

_atprog=None
def drop_at(content):
	if content is None:
		return None,None
	global _atprog
	if _atprog is None:
		import re
		_atprog=re.compile(r"<a\W[^>]+?http://www.renren.com/g/(\d+)[^>]*>(@.*?)</a>",re.DOTALL)
	return _atprog.sub(r'\2(\1)',str(content))

_imgprog=None
def drop_img(content):
	if content is None:
		return None
	global _imgprog
	if _imgprog is None:
		import re
		_imgprog=re.compile(r"<img\W[^>]+alt=\'([^>]*?)\'[^>]*?/>",re.DOTALL)
	return _imgprog.sub(r'(img\1img)',content)

_rrurlprog=None
def drop_rrurl(content):
	if content is None:
		return None
	global _rrurlprog
	if _rrurlprog is None:
		import re
		_rrurlprog=re.compile(r"<a\W[^>]+title='([^>]+)'>[^<]+</a>",re.DOTALL)
	return _rrurlprog.sub(r'(\1)',content)

def split_owner(content):
	if content is None:
		return None,None,None
	else:
		idx=content.replace('：',':').find(':')
		idx2=content.find(',')
		if (idx < 0) or (idx2 <0):
			return None,None,None
		return content[:idx2].strip('( '),content[idx2+1:idx].strip(') '),content[idx+1:].strip(' ')
