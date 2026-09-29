from pathlib import Path
import re, html

base=Path(__file__).parent
out=base/'dist'
(out/'work').mkdir(parents=True,exist_ok=True)
(out/'assets').mkdir(exist_ok=True)
def esc(s): return html.escape(s)
def icon(name):
 svg=(out/'assets/icons'/f'{name}.svg').read_text()
 svg=svg[svg.index('<svg'):]
 return re.sub(r'<svg\b', '<svg class="icon" aria-hidden="true"', svg, count=1)

def chrome(title, content, prefix=''):
 content=content.replace('↗',icon('arrow-up-right')).replace('←',icon('arrow-left')).replace('→',icon('arrow-right'))
 return f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>{esc(title)} | LiquidJelly</title><meta name="description" content="Practical AI consultancy and hands-on software development, grounded in experience."><link rel="icon" href="{prefix}assets/liquidjelly-logo.png"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;450;500;600&display=swap"><link rel="stylesheet" href="{prefix}style.css"></head><body><a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="wrap header-inner"><a href="{prefix}index.html" aria-label="LiquidJelly home"><img class="logo" src="{prefix}assets/liquidjelly-logo.png" alt="LiquidJelly" width="206" height="48"></a><nav aria-label="Main navigation"><a href="{prefix}index.html#consultancy">AI consultancy</a><a href="{prefix}index.html#security">Security</a><a href="{prefix}index.html#experience">Experience</a><a href="{prefix}index.html#about">About</a><a class="nav-contact" href="{prefix}contact.html">Let’s talk</a></nav></div></header>{content}<footer><div class="wrap footer-inner"><span>LiquidJelly Ltd · AI consultancy & software development</span><span>Registered in England & Wales · 07530917</span><a href="{prefix}credits.html">Image credits</a><a href="mailto:hello@liquidjelly.co.uk">hello@liquidjelly.co.uk</a></div></footer><script src="{prefix}script.js"></script></body></html>'''

source=(base/'content/case-studies.md').read_text()
titles=[c.splitlines()[0] for c in re.split(r'\n## \d+\. ',source)[1:]]
cases=[]
slugs=['nhs-integration','application-framework','branch-till-reporting','parcel-booking','iconsign-modernisation','tracking-portals','team-leadership']
for i,chunk in enumerate(re.split(r'\n## \d+\. ',source)[1:]):
 title=chunk.splitlines()[0]
 metadata=dict(re.findall(r'\*\*(Organisation|Project|Product|Assignment|Dates|Role):\*\* (.+)',chunk))
 org=metadata['Organisation'].strip()
 if i==4: org='DHL / UK Mail'
 if i==5: org='UK Mail / DHL contract history'
 excerpt=re.search(r'\*\*Homepage excerpt:\*\* (.+)',chunk).group(1)
 sections=[]
 for section in re.split(r'\n### ',chunk)[1:]:
  heading,body=section.split('\n',1)
  heading=heading.replace('Mark’s contribution','Our contribution')
  body=body.split('**Homepage excerpt:**')[0].strip()
  body=body.replace('Mark’s work','Our work').replace('Mark’s 2005–2011 employment','our earlier 2005–2011 employed experience')
  body=re.sub(r'\b(?:Mark|He)\b', 'We', body)
  body=re.sub(r'\bhe\b', 'we', body)
  sections.append(f'<section class="case-section"><h2>{esc(heading)}</h2>'+''.join('<p>'+esc(p)+'</p>' for p in body.split('\n\n'))+'</section>')
 previous=(i-1)%len(slugs)
 following=(i+1)%len(slugs)
 case_nav=f'<nav class="case-navigation wrap" aria-label="Case studies"><a rel="prev" href="{slugs[previous]}.html"><span>← Previous project</span><strong>{esc(titles[previous])}</strong></a><a rel="next" href="{slugs[following]}.html"><span>Next project →</span><strong>{esc(titles[following])}</strong></a></nav>'
 content=f'''<main id="main"><section class="case-hero wrap"><a class="back" href="../index.html#experience">← Selected experience</a><p class="eyebrow">DEVELOPMENT CASE STUDY / {i+1:02}</p><h1>{esc(title)}</h1><div class="case-meta"><div><span>Organisation</span>{esc(org)}</div><div><span>Project dates</span>{esc(metadata['Dates'])}</div><div><span>Role</span>{esc(metadata['Role'])}</div></div></section><div class="case-body wrap"><aside><p class="eyebrow">THE WORK</p><p>{esc(excerpt)}</p><p class="small">Historical software development experience.</p></aside><article>{''.join(sections)}</article></div>{case_nav}<section class="case-contact wrap"><h2>Working through a similar challenge?</h2><a class="button" href="../contact.html">Talk through your project ↗</a></section></main>'''
 (out/'work'/f'{slugs[i]}.html').write_text(chrome(title,content,'../'))
 cases.append({'title':title,'org':org,'date':metadata['Dates'],'excerpt':excerpt,'slug':slugs[i]})

brands=[
('PHOENIX Medical Supplies','Contract projects · healthcare','phoenix.svg'),
('DHL / UK Mail','Contract projects · logistics','dhl.svg'),
('O2','UK Mail customer platform','o2.svg'),
('Vodafone','UK Mail customer platform','vodafone.svg'),
('EE','UK Mail customer platform','ee.png'),
('BT','UK Mail returns platform','bt.svg'),
('Orange','UK Mail customer platform','orange.svg'),
('Three','Earlier telecom experience','three.png'),
('Argos','Earlier retail experience','argos.svg'),
('Aviva','Earlier financial-services experience','aviva.svg'),
('Nationwide','Earlier financial-services experience','nationwide.svg'),
('Legal & General','Earlier financial-services experience','legalgeneral.svg'),
('Co-op Financial Services','Earlier financial-services experience','coop.svg'),
('Rolls-Royce','Earlier engineering experience','rollsroyce.svg'),
('Diesel','UK Mail customer platform','diesel.png'),
('Superdry','Earlier retail experience','superdry.jpg'),
('Cotswold Outdoor','Earlier retail experience','cotswold.jpg'),
('Crimson','Contract projects · health & safety','crimson.svg'),
('Pin Digital','Earlier employed experience','pindigital.svg')]
# Keep CV-era names and relationships; use plain type when no matching logo is available.
extra_brands=[
('eg Solutions','Employed roles · 2005–2011',None),
('Wesleyan','Earlier financial-services experience',None),
('Lafferty International','Earlier financial-services experience',None),
('UK Mail','Contract roles · 2011–2016',None),
('iPostParcels','UK Mail ecommerce platform',None),
('Stewart Grand Prix','Earlier engineering experience',None),
('Mallock Engineering','Earlier engineering experience',None),
('ATC Derby','Employed engineering role · 1998–2000',None),
('ATC Belcan','Earlier engineering experience',None),
('Rowlands Pharmacy','Pharmacy systems experience',None),
('Cotswold Group','UK Mail customer platform',None),
('SuperGroup','UK Mail customer platform',None),
('NEC Technologies','University work placement',None),
('Southalls Safety Cloud','Product work through Crimson',None)]
brands+=extra_brands
brand_lookup={name:(detail,file) for name,detail,file in brands}
sectors=[
('Communications',['O2','Vodafone','EE','BT','Orange','Three']),
('Finance',['eg Solutions','Aviva','Nationwide','Legal & General','Co-op Financial Services','Wesleyan','Lafferty International']),
('Logistics',['DHL / UK Mail','UK Mail','iPostParcels']),
('Motorsports / Aerospace',['Rolls-Royce','Stewart Grand Prix','Mallock Engineering','ATC Derby','ATC Belcan']),
('Healthcare',['PHOENIX Medical Supplies','Rowlands Pharmacy']),
('Retail',['Argos','Diesel','Cotswold Group','SuperGroup']),
('Software & Technology',['Crimson','Pin Digital','NEC Technologies','Southalls Safety Cloud'])]
items=[]
for sector,names in sectors:
 sector_id=sector.lower().split(' / ')[0].replace(' & ','-')
 for name in names:
  detail,file=brand_lookup[name]
  if sector=='Logistics': link='work/parcel-booking.html'
  elif sector=='Healthcare': link='work/nhs-integration.html'
  elif name=='eg Solutions': link='work/team-leadership.html'
  else: link='sectors.html#'+sector_id
  mark=f'<img src="assets/logos/{file}" alt="" width="150" height="54">' if file else f'<span class="company-wordmark">{esc(name)}</span>'
  items.append(f'<li><a href="{link}"><span class="sector-mark">{mark}</span><span>{esc(name)}</span><small>{esc(detail)}</small></a></li>')
# Keep all company cards on one continuous ribbon, with one accessible copy.
group=''.join(items)
duration=len(items)*200/30
sectorhtml=f'<div class="sector company-ribbon"><div class="sector-window"><div class="marquee-track sector-track" style="--sector-duration:{duration:.1f}s"><ul>{group}</ul><ul aria-hidden="true" inert>{group}</ul></div></div></div>'

services=[('01','Find the right starting point','AI advice & discovery','Identify where AI could help and what it would take to use it. Work through your data, costs and constraints, then define a focused first project.','A clear scope and a way to measure success.'),('02','Test it against real work','Prototypes & feasibility','Try the idea with representative tasks. Explore where it performs well, where it struggles and whether it warrants further investment.','A working prototype and evidence for the next decision.'),('03','Connect it to your business','AI integration & automation','Bring AI into existing applications and workflows, with appropriate permissions, review steps and a record of what happened.','One connected workflow, ready to test and improve.'),('04','Help your team put it to use','AI-assisted development','Introduce AI into coding, testing and documentation with practical guidance. Keep review, testing and responsibility clear.','A team workflow tried on real development work.')]
servicehtml=''.join(f'<article class="service-row"><div><p class="eyebrow subsection-label">{icon(["search","flask-conical","workflow","code-xml"][int(n)-1])}<span>01 / {n} {label}</span></p><h3>{title}</h3></div><div><p>{copy}</p><p class="outcome">{outcome}</p></div></article>' for n,title,label,copy,outcome in services)
casehtml=''.join(f'<a class="work-item" href="work/{cases[i]["slug"]}.html"><div><p class="eyebrow">03 / {j+1:02} {esc(cases[i]["org"])}</p><div class="work-heading"><img class="work-logo" src="assets/logos/{"ukmail.svg" if i==3 else "phoenix.svg"}" alt="" width="160" height="60"><h3>{esc(cases[i]["title"])}</h3></div><p>{esc(cases[i]["excerpt"])}</p><span class="small">{esc(cases[i]["date"])}</span></div><span class="work-arrow" aria-hidden="true">↗</span></a>' for j,i in enumerate([0,1,3]))
morehtml=''.join(f'<a href="work/{cases[i]["slug"]}.html"><span><span class="project-number">03 / {j+4:02}</span> {esc(cases[i]["title"])}</span><span aria-hidden="true">↗</span></a>' for j,i in enumerate([2,4,5,6]))
home=f'''<main id="main"><section class="hero"><div class="wrap hero-grid"><div><p class="eyebrow">AI CONSULTANCY & SOFTWARE DEVELOPMENT</p><h1><span class="sr-only">A practical approach to AI. An experienced hand in design, development, testing and deployment.</span><span aria-hidden="true">A practical approach to AI.<br><span class="hero-secondary">An experienced hand in <span class="typing-line"><span id="typed-word">development</span><span class="typing-cursor">|</span></span></span></span></h1><p class="hero-copy">Make sense of where AI can help, test an idea against real work, and build it into the systems your business depends on.</p><div class="hero-actions"><a class="button" href="contact.html">Talk through your idea ↗</a><a class="text-link" href="#experience">Explore the work</a></div></div><aside class="hero-note lifecycle-visual" aria-label="Our software lifecycle"><p class="eyebrow">FROM IDEA TO OPERATION</p><div class="lifecycle-core">{icon("workflow")}<span>Considered.<br>Connected.<br>Built to last.</span></div><div class="lifecycle-stages"><span>{icon("search")}Design</span><span>{icon("code-xml")}Develop</span><span>{icon("flask-conical")}Test</span><span>{icon("server")}Deploy</span></div></aside></div><div class="wrap hero-bottom"><span>Independent advice. Hands-on delivery.</span><span>Building web applications since 2000</span></div></section>
<section class="experience-strip" aria-label="Previous organisations"><div class="wrap strip-heading"><div><h2>Experience built in real businesses</h2><p>Experience across contracts, employed roles and customer platforms.</p></div></div><div class="wrap sector-grid">{sectorhtml}</div><div class="wrap additional-experience"><p>Organisations and customer brands from our wider project history; relationships vary by assignment.</p></div></section>
<section class="wrap section" id="consultancy"><div class="section-intro"><p class="eyebrow">01 / PRACTICAL AI</p><div><h2>Find a useful<br>starting point.</h2><p>You may have an idea for AI, a process that takes too long, or a team weighing up new tools. Start with the work itself and what needs to improve.</p></div></div><div class="services">{servicehtml}</div></section>
<section class="engineering" id="development"><div class="wrap engineering-grid"><div><p class="eyebrow">02 / THE ENGINEERING</p><h2>The software around<br>the AI matters.</h2></div><div><p class="lead">Reliable data. Sensible permissions. Systems that work together.</p><p>LiquidJelly combines consultancy with application development, API integration and legacy modernisation. The same conversation can cover the idea, the software around it and how it will be supported.</p><ul class="capabilities"><li>Bespoke business applications</li><li>APIs & system integration</li><li>Legacy modernisation</li><li>Testing & delivery pipelines</li></ul></div></div></section>
<section class="security" id="security"><div class="wrap security-grid"><div><p class="eyebrow">SECURITY / PRIVACY / CONTROL</p><h2>Your data.<br>Your boundaries.</h2><p class="lead">We help you choose where AI runs, what it can access and what stays under your control.</p><div class="data-boundary" role="img" aria-label="Illustrative private AI architecture: business data and a local model within a controlled environment, with an approved connection to external services"><div class="boundary-label">{icon("shield-check")} YOUR CONTROLLED ENVIRONMENT</div><div class="boundary-nodes"><span>{icon("database")}Business data</span>{icon("arrow-right")}<span>{icon("server")}Local AI</span></div><div class="boundary-gate">{icon("lock-keyhole")} Approved connections only</div><div class="boundary-cloud">{icon("cloud")}External services, when needed</div></div></div><div class="security-points"><article>{icon("server")}<div><h3>Local and private AI</h3><p>We assess tools that run on your own hardware or in a private environment. We check model access, telemetry, updates and external connections, so “local” is a deliberate setup rather than an assumption.</p></div></article><article>{icon("lock-keyhole")}<div><h3>Protect the information you use</h3><p>We design for limited access, appropriate encryption, retention controls and a clear audit trail. We review what providers do with prompts, uploaded files and outputs, including whether they may be used for training.</p></div></article><article>{icon("globe")}<div><h3>Data sovereignty and location</h3><p>We consider where information is stored and processed, who can access it and which jurisdictions apply. Hosting region, support access, subprocessors and international transfers all form part of that decision.</p></div></article><article>{icon("file-check-2")}<div><h3>Regulatory requirements, considered early</h3><p>We work with your security and data-protection teams to address UK GDPR, relevant sector requirements and impact assessments where needed. Local deployment alone does not establish compliance.</p></div></article></div></div></section>
<section class="wrap section" id="experience"><div class="section-intro"><p class="eyebrow">03 / SELECTED EXPERIENCE</p><div><h2>Built for the work<br>people actually do.</h2><p>Our development experience spans business systems, integration and technical leadership, across contract and earlier employed roles.</p></div></div><div class="selected-work">{casehtml}</div><details class="more-work"><summary>Explore four more projects {icon("chevron-down")}</summary><div>{morehtml}</div></details></section>
<section class="approach"><div class="wrap"><div class="section-intro"><p class="eyebrow">04 / THE APPROACH</p><h2>Start small.<br>Make the next decision<br>with evidence.</h2></div><ol class="steps"><li><h3 class="eyebrow">04 / 01 Understand</h3><p>Agree the problem, the constraints and what a useful result looks like.</p></li><li><h3 class="eyebrow">04 / 02 Prove</h3><p>Test the riskiest assumptions with a focused piece of work.</p></li><li><h3 class="eyebrow">04 / 03 Build</h3><p>Develop and integrate, with regular review and testing.</p></li><li><h3 class="eyebrow">04 / 04 Improve</h3><p>Use feedback and operational evidence to guide what happens next.</p></li></ol></div></section>
<section class="wrap section about" id="about"><p class="eyebrow">05 / ABOUT LIQUIDJELLY</p><div><h2>Experience, applied.</h2><p class="lead">We bring experience building web applications since 2000 to the opportunities AI creates today.</p><p>Our work spans pharmacy systems, parcel logistics, ecommerce and enterprise applications. We have worked independently, alongside established teams and in technical leadership roles, helping developers adopt new tools and practices.</p><p>That background shapes our approach: understand the business, make considered technical choices and take responsibility for the work.</p></div></section>
<section class="contact" id="contact"><div class="wrap contact-grid"><div><p class="eyebrow">LET’S TALK</p><h2>What would you<br>like to make easier?</h2></div><div><p>Bring a process, a project or a question about AI. We can talk through the options and work out a sensible first step.</p><p><a class="button" href="contact.html">Talk through your idea ↗</a></p><a href="mailto:hello@liquidjelly.co.uk" class="contact-email">Prefer email? hello@liquidjelly.co.uk ↗</a></div></div></section></main>'''
(out/'index.html').write_text(chrome('AI Consultancy & Software Development',home))
print(f'Created homepage and {len(cases)} case study pages in {out}')

privacy='<main id="main" class="wrap section"><p class="eyebrow">PRIVACY</p><h1>Your enquiry and your data</h1><div class="privacy-copy"><p>LiquidJelly Ltd uses the name, email address, company and message you provide to understand your enquiry and respond to it. We do not add enquiry details to a marketing list.</p><h2>How your enquiry is handled</h2><p>Our website and enquiry service use Cloudflare. Submitted details are stored in a private Cloudflare D1 database and are accessible to authorised administrators. Cloudflare Turnstile checks submissions to help prevent spam and may process technical information about your browser and connection.</p><p>We process enquiries to take steps at your request before entering a contract, or for our legitimate interest in responding to business enquiries. Enquiries are deleted from the website database after 12 months. If we work together, information needed for the engagement may be retained separately.</p><h2>Your choices</h2><p>To request access, correction or deletion, or to ask about how your information is used, email <a href="mailto:hello@liquidjelly.co.uk">hello@liquidjelly.co.uk</a>. You can also raise concerns with the UK Information Commissioner’s Office.</p><p>Please do not submit passwords, confidential customer records or sensitive personal information through this form.</p><a href="contact.html">Return to your enquiry</a></div></main>'
(out/'privacy.html').write_text(chrome('Enquiry privacy',privacy))

sectorcopy='<main id="main" class="wrap section"><p class="eyebrow">EXPERIENCE BY SECTOR</p><h1>Different industries.<br>Practical engineering.</h1><div class="privacy-copy"><section id="communications"><h2>Communications</h2><p>Our UK Mail project history includes an inter-branch transfer platform for O2, developed between February 2013 and January 2014, with branded variants for Orange, EE and Vodafone. A separate returns portal helped BT customers arrange hardware swap-outs. These were customer platforms delivered through UK Mail.</p><p>Our wider telecoms experience also includes Three.</p></section><section id="finance"><h2>Finance</h2><p>Our earlier experience includes Aviva, Nationwide, Legal &amp; General, Co-op Financial Services, Wesleyan and Lafferty International. These names represent our wider career history, including earlier employed roles, rather than separate current AI consultancy engagements.</p><p><a href="work/team-leadership.html">Explore our technical leadership experience</a></p></section><section id="logistics"><h2>Logistics</h2><p>UK Mail and DHL projects covered parcel booking, labels, payments, tracking, returns and the modernisation of operational software.</p><p><a href="work/parcel-booking.html">Read the parcel-booking case study</a></p></section><section id="motorsports"><h2>Motorsports / Aerospace</h2><p>Our earlier engineering experience includes Rolls-Royce, Stewart Grand Prix, Mallock Engineering and ATC Belcan. These organisations form part of our wider career history; company-specific project dates and outcomes are not presented as verified case studies.</p></section><section id="healthcare"><h2>Healthcare</h2><p>PHOENIX Medical Supplies projects span pharmacy systems, patient safety, branch reporting and integration. NHS and EMIS are integration targets in that work, rather than separate client engagements.</p></section><section id="retail"><h2>Retail</h2><p>The UK Mail inter-branch transfer system was adapted for Cotswold Group, Diesel and SuperGroup. Our wider earlier retail experience includes Argos.</p></section><section id="software-technology"><h2>Software &amp; Technology</h2><p>Our CV includes contract development with Crimson IT Solutions on Southalls Safety Cloud, ecommerce development at Pin Digital from 2003 to 2005, and a university placement with NEC Technologies. These represent different kinds of experience, with the relationship identified on each company card.</p></section><p><a href="contact.html">Talk through your idea</a></p></div></main>'
(out/'sectors.html').write_text(chrome('Experience by sector',sectorcopy))

contact=f'''<main id="main" class="contact enquiry-page"><div class="wrap contact-grid"><div><p class="eyebrow">LET’S TALK</p><h1>Talk through<br>your idea.</h1><p class="lead">What would you like to make easier?</p><p>Bring a process, a project or a question about AI. Tell us a little about what you have in mind and we’ll work out a sensible first step.</p><a href="mailto:hello@liquidjelly.co.uk" class="contact-email">Prefer email? hello@liquidjelly.co.uk ↗</a></div><div><form id="idea-form" class="idea-form" action="/api/enquiries" method="post"><div class="form-pair"><label>Your name<input name="name" autocomplete="name" required maxlength="100"></label><label>Email address<input name="email" type="email" autocomplete="email" required maxlength="254"></label></div><label>Company <span>(optional)</span><input name="company" autocomplete="organization" maxlength="150"></label><label>What would you like to explore?<select name="interest" required><option value="">Choose an area</option><option>AI advice & discovery</option><option>Prototypes & feasibility</option><option>AI integration & automation</option><option>Software development</option><option>Something else</option></select></label><label>Tell us a little about your idea<textarea name="message" rows="5" minlength="20" maxlength="5000" required placeholder="What are you trying to improve, and where could we help?"></textarea></label><div class="form-trap" aria-hidden="true"><label>Leave this empty<input name="website" tabindex="-1" autocomplete="off"></label></div><p class="form-privacy">We’ll use your details to respond to this enquiry. Please leave out passwords, customer records and other sensitive information. <a href="privacy.html">How we handle your data</a>.</p><div id="turnstile-widget"></div><button class="button" type="submit">Send your idea {icon("arrow-right")}</button><p id="form-status" role="status" aria-live="polite"></p><noscript><p>Please enable JavaScript to send this form, or email us below.</p></noscript></form></div></div></main>'''
(out/'contact.html').write_text(chrome('Talk through your idea',contact))

credits='<main id="main" class="wrap section"><p class="eyebrow">IMAGE CREDITS</p><h1>Company marks</h1><div class="privacy-copy"><p>The UK Mail logo asset is by <a href="https://commons.wikimedia.org/wiki/User:MillieCoutts">MillieCoutts</a>, from <a href="https://commons.wikimedia.org/wiki/File:UK_Mail_logo2.svg">Wikimedia Commons</a>, licensed under <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>. It is displayed in greyscale; the source SVG is unchanged.</p><p>Company names and trademarks belong to their respective owners. They identify organisations from our project and career history.</p><a href="index.html#experience">Back to selected experience</a></div></main>'
(out/'credits.html').write_text(chrome('Image credits',credits))
