import React, { useEffect, useState } from "react";
import { useHistory } from "react-router-dom";
import { Container, Grid } from "@material-ui/core";
import { Steps } from 'intro.js-react';

const ViewReport = (props) => {
	console.log(props);
	const [stepsEnabled, setStepsEnabled] = useState(true);
	const steps = [{
		element: '#card',
		intro: 'Intel Report Details'
	}]
	const history = useHistory();

	useEffect(()=>{
		if(props.intelgroup.id != props.currentgroup)
			history.push('/intelreports');
	},[props.currentgroup])

	let tags = [];
	if(props.groupfeed.tags){
		if(props.groupfeed.tags.indexOf(",") > -1)
		tags = props.groupfeed.tags.split(',');
		else tags.push(props.groupfeed.tags);
	}
	const classifications = [];
	props.classifications.forEach(classification => {
		if(classification.intelgroup.id == props.intelgroup.id){
			classifications.push(classification);
		}
	});
	const indicators = [];
	props.indicators.forEach(indicator => {
		if(props.feeditem.id == indicator.feeditem_id){
			indicators.push(indicator)
		}
	});
	let ip=[], system=[], infrastructure=[], analysis=[], hash=[];
	indicators.forEach(indicator => {
		if(indicator.globalindicator.type == 'IP'){
			let obj = {};
			obj[indicator.globalindicator.value]=indicator.value
			ip.push(obj);
		}
		else if(indicator.globalindicator.type == 'System'){
			let obj = {};
			obj[indicator.globalindicator.value]=indicator.value;
			system.push(obj);
		}
		else if(indicator.globalindicator.type == 'Infrastructure'){
			let obj = {};
			obj[indicator.globalindicator.value]=indicator.value
			infrastructure.push(obj);
		}
		else if(indicator.globalindicator.type == 'Analysis'){
			let obj = {};
			obj[indicator.globalindicator.value]=indicator.value
			analysis.push(obj);
		}
		else if(indicator.globalindicator.type == 'Hash'){
			let obj = {};
			obj[indicator.globalindicator.value]=indicator.value
			hash.push(obj);
		}
	});
	let gthreattype=[], gthreatactor=[], gcountry=[], gproduct=[], gsector=[];
	props.globalattributes.forEach(globalattribute => {
		if(globalattribute.globalattribute.attribute == 'Threat type'){
			let obj = {};
			obj[globalattribute.globalattribute.value]=globalattribute.globalattribute.words_matched
			gthreattype.push(obj);
		}
		else if(globalattribute.globalattribute.attribute == 'Threat actor'){
			let obj = {};
			obj[globalattribute.globalattribute.value]=globalattribute.globalattribute.words_matched
			gthreatactor.push(obj);
		}
		else if(globalattribute.globalattribute.attribute == 'Country'){
			let obj = {};
			obj[globalattribute.globalattribute.value]=globalattribute.globalattribute.words_matched
			gcountry.push(obj);
		}
		else if(globalattribute.globalattribute.attribute == 'Product'){
			let obj = {};
			obj[globalattribute.globalattribute.value]=globalattribute.globalattribute.words_matched
			gproduct.push(obj);
		}
		else if(globalattribute.globalattribute.attribute == 'Sector'){
			let obj = {};
			obj[globalattribute.globalattribute.value]=globalattribute.globalattribute.words_matched
			gsector.push(obj);
		}
	});
	let global = {};
	if(gthreattype.length > 0) global['Threat_type'] = gthreattype;
	if(gthreatactor.length > 0) global['Threat_actor'] = gthreatactor;
	if(gproduct.length > 0) global['Product'] = gproduct;
	if(gcountry.length > 0) global['Country'] = gcountry;
	if(gsector.length > 0) global['Sector'] = gsector;
	let cthreattype=[], cthreatactor=[], ccountry=[], cproduct=[], csector=[];
	classifications.forEach(classification => {
		if(classification.attribute == 'Threat type'){
			let obj = {};
			obj[classification.value]=classification.words_matched
			cthreattype.push(obj);
		}
		else if(classification.attribute == 'Threat actor'){
			let obj = {};
			obj[classification.value]=classification.words_matched
			cthreatactor.push(obj);
		}
		else if(classification.attribute == 'Country'){
			let obj = {};
			obj[classification.value]=classification.words_matched
			ccountry.push(obj);
		}
		else if(classification.attribute == 'Product'){
			let obj = {};
			obj[classification.value]=classification.words_matched
			cproduct.push(obj);
		}
		else if(classification.attribute == 'Sector'){
			let obj = {};
			obj[classification.value]=classification.words_matched
			csector.push(obj);
		}
	});
	let intel = {};
	if(cthreattype.length > 0) intel['Threat_type'] = cthreattype;
	if(cthreatactor.length > 0) intel['Threat_actor'] = cthreatactor;
	if(cproduct.length > 0) intel['Product'] = cproduct;
	if(ccountry.length > 0) intel['Country'] = ccountry;
	if(csector.length > 0) intel['Sector'] = csector;
	const data = {
		UUID: props.uniqueid,
		Intel_Group_UUID: props.intelgroup.id,
		Report_URL: `https://sherlock-staging.obstractai.com/api/v1/reports?UUID=${props.uniqueid}`,
		Datetime_added: props.created_at,
		RSS_data: {
			Title:props.feeditem.title,
			Link:props.feeditem.link,
			Description:props.feeditem.description,
			Author:props.feeditem.author,
			Category:props.feeditem.category,
			Comments:props.feeditem.comments,
			Enclosure:props.feeditem.enclosure,
			Guid:props.feeditem.guid,
			pubDate:props.feeditem.pubdate,
			Source:props.feeditem.source,
		},
		Indicators: {
			IP:ip,
			System:system,
			Infrastructure:infrastructure,
			Analysis:analysis,
			Hash:hash
		},
		Attributes: {
			Global:global,
			Intel_Group:intel,
		}
	}
	
	useEffect(()=>{
		let str=props.feeditem.description;
		indicators.forEach(indicator => {
			let items = indicator.value.split(',');
			items.forEach(item => {
				if(!(item*1>0 && item*1<10) && item.indexOf('?') == -1){
					item = item.replace(/'/gi, "").replace(/\\/gi, "").trim();
					let reg = new RegExp(item, 'g'), result, ids = [];
					while ( (result = reg.exec(str)) ) {
						ids.push(result.index);
					}
					for(let i=0;i<ids.length;i++) {
						let astartreg = />/gi, alastreg = /</gi, re, astart = [], alast = [];
						while ( (re = astartreg.exec(str)) ) {
							astart.push(re.index);
						}
						while ( (re = alastreg.exec(str)) ) {
							alast.push(re.index);
						}
						for(let j=0;j<astart.length-1;j++){
							if(ids[i] >= astart[j] && ids[i] <= alast[j+1]){
								let flag = true
								if(indicator.globalindicator.value == 'IPv4'){
									if((str.substr(ids[i]+item.length, 1)*1 > 0 && str.substr(ids[i]+item.length, 1)*1 < 9) || str.substr(ids[i]+item.length, 1) == '/'){
										flag = false
									}
								}
								if(indicator.globalindicator.value == 'FQDN'){
									if(str.substr(ids[i]-1, 1) == '.' || str.substr(ids[i]-1, 1) == '/' || str.substr(ids[i]-1, 1) == '@'){
										flag = false
									}
								}
								if(flag){
									let target = "<span style='background:#faeb42;'>" + item + "</span>";
									let target1 = `<Tooltip title='indicator = ${indicator.globalindicator.value}'>${target}</Tooltip>`;
									str = str.substring(0, ids[i]) + target1 + str.substr(ids[i]+item.length);
									for(let k=i+1;k<ids.length;k++){
										ids[k] = ids[k] + target1.length - item.length;
									}
								}
							}
						}
					};
				}
			});
			if(indicator.globalindicator.value == 'Filename'){
				let items = indicator.value.split(',');
				let imgstart = new RegExp('<img', 'gi'), result, start = [], last=[];
				while ( (result = imgstart.exec(str)) ) {
					start.push(result.index);
				}
				start.forEach(s => {
					for(let i=0;i<str.length;i++){
						let p=0
						if(str[i] == '>' && i > s){
							p++;
							if(p == 1){
								last.push(i);
								break;
							}
						}
					}
				});
				for(let i=0;i<start.length;i++){
					let temp=[];
					items.forEach(item => {
						let reg = new RegExp(item, 'gi'), result, ids=[];
						while ( (result = reg.exec(str)) ) {
							ids.push(result.index);
						}
						if(ids[0]>start[i] && ids[0]<last[i]){
							temp.push(item);
						}
					});
					let target = str.substring(start[i], last[i]+1);
					let target1 = `<Tooltip title="indicator = ${indicator.globalindicator.value}">${target}</Tooltip>`;
					// let target1 = `<Tooltip title="${indicator.globalindicator.value}=${temp.join(',')}">${target}</Tooltip>`;
					for(let j=i+1;j<start.length;j++){
						start[j] = start[j] + target1.length-target.length;
						last[j] = last[j] + target1.length-target.length;
					}
					str = str.replace(target, target1)
				}
			}
		});
		
		let words = [];
		classifications.forEach(classification => {
			if(classification.words_matched.indexOf(",")>-1){
				let temp = classification.words_matched.split(",");
				words = words.concat(temp);
			}
			else words.push(classification.words_matched);
		});
		props.globalattributes.forEach(globalattribute => {
			if(globalattribute.globalattribute.words_matched.indexOf(",")>-1){
				let temp = globalattribute.globalattribute.words_matched.split(",");
				words = words.concat(temp);
			}
			else words.push(globalattribute.globalattribute.words_matched);
		});
		words.forEach(word => {
			let reg = new RegExp(word.trim(), "g"), result, ids = [];
			while ((result = reg.exec(str))) {
				ids.push(result.index);
			}
			for(let i=0;i<ids.length;i++) {
				let astartreg = />/gi, alastreg = /</gi, re, astart = [], alast = [];
				while ( (re = astartreg.exec(str)) ) {
					astart.push(re.index);
				}
				while ( (re = alastreg.exec(str)) ) {
					alast.push(re.index);
				}
				for(let j=0;j<astart.length-1;j++){
					if(ids[i] >= astart[j] && ids[i] <= alast[j+1]){
						let target = `<span style="background:#00e7ff;">${word.trim()}</span>`;
						str = str.substring(0, ids[i]) + target + str.substr(ids[i]+word.trim().length);
						for(let k=i+1;k<ids.length;k++){
							ids[k] = ids[k] + target.length - word.trim().length;
						}
					}
				}
			}
		});
		document.querySelector("#extraction").innerHTML=str;

	},[]);
	return (
		<Container>
			{props.mygroups.length == 0 &&
			<Steps
				enabled={stepsEnabled}
				steps={steps}
				initialStep={0}
				onExit={(index)=>{
					setStepsEnabled(false);
				if(index==0)
					window.location.href='/home/extractions';
				}}
				options={{
					doneLabel: 'Next'
				}}
			/>}
			<section className="section">
				<Grid container>
					<Grid item xs={12} md={6}>
						<h1 className="title is-2">{props.feeditem.title}</h1>
					</Grid>
					<Grid item xs={12} md={6}>
						<span>
							<button className="button is-info is-rounded mx-2">
								<span>{props.groupfeed.category.name}</span>
							</button>
							{tags.map((tag, index)=>{
								return <button key={index} className="button is-warning is-rounded mx-2" >
									<span>{tag}</span>
								</button>
							})}
							<button className="button is-danger is-rounded mx-2" >
								<span>{props.groupfeed.name}</span>
							</button>
							<button className="button is-primary is-rounded mx-2" >
								<span>{props.groupfeed.confidence}</span>
							</button>
						</span>
					</Grid>
				</Grid>
			</section>
			<section className="section">
				<button className="button is-info is-pulled-left" onClick={()=>history.goBack()}>Back</button>
			</section>
			<section>
				<Grid container id="card">
					<Grid item xs={12} id="extraction">
						
					</Grid>
					<Grid item xs={12} className="section">
						<section className="section app-card">
							<Grid container>
								<Grid item xs={3} className="pt-4">
									<span>Confidence:</span>
								</Grid>
								<Grid item xs={9} className="py-2">
									<button className="button is-primary is-rounded" >
										<span>{props.groupfeed.confidence}</span>
									</button>
								</Grid>
							</Grid>
							<Grid container>
								<Grid item xs={3} className="pt-4">
									<span>Observables:</span>
								</Grid>
								<Grid item xs={9}>
									{props.globalattributes.map((classification, index)=>{
										return <button key={index} className="button is-warning is-rounded mx-1 my-1">
											<span>{classification.globalattribute.words_matched}</span>
										</button>
									})}
									{classifications.map((classification, index)=>{
										return <button key={index} className="button is-warning is-rounded mx-1 my-1" >
											<span>{classification.words_matched}</span>
										</button>
									})}
								</Grid>
							</Grid>
							<Grid container>
								<Grid item xs={3} className="pt-4">
									<span>Indicators:</span>
								</Grid>
								<Grid item xs={9} className="py-2">
									{indicators.map((indicator, index)=>{
										return <button key={index} className="button is-success is-rounded mx-1	my-1" >
											<span>{indicator.globalindicator.value}</span>
										</button>
									})}
								</Grid>
							</Grid>
							<p>JSON object: </p>
							<pre>{JSON.stringify(data, null, 2)}</pre>
							<p>API Call</p>
							<div>
								<span>Feed: </span>
								<span>https://sherlock-staging.obstractai.com/api/v1/feeds?UUID={props.groupfeed.uniqueid}</span>
							</div>
							<div>
								<span>Report: </span>
								<span>https://sherlock-staging.obstractai.com/api/v1/reports?UUID={props.uniqueid}</span>
							</div>
							<a href="/api/docs" className="muted-link">API docs</a>
						</section>
					</Grid>
				</Grid>
			</section>
		</Container>
	);
}

export default ViewReport;