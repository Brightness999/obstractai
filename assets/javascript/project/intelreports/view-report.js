import React, { useEffect } from "react";
import { useHistory } from "react-router-dom";
import { Container, Grid } from "@material-ui/core";

const ViewReport = (props) => {
	console.log(props);
	const history = useHistory();
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
	
	useEffect(()=>{
		let str=props.feeditem.description;
		
		indicators.forEach(indicator => {
			if(indicator.globalindicator.value == 'CVE'){
				let items = indicator.value.split(',');
				items.forEach(item => {
					let reg = new RegExp('>'+item+'<', 'g'), result, ids = [];
					while ( (result = reg.exec(str)) ) {
						ids.push(result.index);
					}
					for(let i=0;i<ids.length;i++){
						let target = str.substring(ids[i], ids[i]+item.length+2);
						let target1 = "<span style='background:#faeb42;'>" + item + "</span>";
						let target2 = `><Tooltip title='${indicator.globalindicator.value}=${item}'>${target1}</Tooltip><`;
						for(let j=i+1;j<ids.length;j++){
							ids[j] = ids[j] + target2.length - target.length;
						}
						str = str.replace(target, target2);
					}
				});
			}
			if(indicator.globalindicator.value == 'URL' || indicator.globalindicator.value == 'Email Address' || indicator.globalindicator.value == 'FQDN'){
				let items = indicator.value.split(',');
				items.forEach(item => {
					let astartreg = /<a/gi, alastreg = /a>/gi, result, astart = [], alast = [];
					while ( (result = astartreg.exec(str)) ) {
						astart.push(result.index);
					}
					while ( (result = alastreg.exec(str)) ) {
						alast.push(result.index);
					}
					let url = item.replace(/'/gi, "").replace(/\\/gi, "").trim();
					if(url.search(RegExp('x(.)?'))>-1)
						url = url.substring(0,url.search(RegExp('x(.)?')))
					let re = new RegExp(url);
					let index = str.search(re);
					for(let i=0;i<astart.length;i++){
						let target = '';
						if(index>astart[i] && index<alast[i]){
							target = str.substring(astart[i], alast[i]+2);
							let target1 = target.substring(0,2) + " style='background:#faeb42;'" + target.substr(2);
							str = str.replace(target, `<Tooltip title="${indicator.globalindicator.value}=${url}">${target1}</Tooltip>`)
						}
					}
				});
			}
			if(indicator.globalindicator.value == 'Topic'){
				let items = indicator.value.split(',');
				items.forEach(item => {
					let reg = new RegExp(item, 'gi'), result, ids = [];
					while ( (result = reg.exec(str)) ) {
						ids.push(result.index);
					}
					for(let i=0;i<ids.length;i++){
						let target = "<span style='background:#faeb42;'>" + item + "</span>";
						let target1 = `<Tooltip title="${indicator.globalindicator.value}=${item}">${target}</Tooltip>`;
						for(let j=i+1;j<ids.length;j++){
							ids[j] = ids[j] + target1.length - target.length;
						}
						str = str.replace(target, target1);
					}
				});
			}
			if(indicator.globalindicator.value == 'SHA256'){
				let items = indicator.value.split(',');
				items.forEach(item => {
					let reg = new RegExp(item, 'gi'), result, ids = [];
					while ( (result = reg.exec(str)) ) {
						ids.push(result.index);
					}
					for(let i=0;i<ids.length;i++){
						let target = str.substring(ids[i], ids[i]+item.length);
						let target1 = "<span style='background:#faeb42;'>" + target + "</span>";
						let target2 = `<Tooltip title="${indicator.globalindicator.value}=${item}">${target1}</Tooltip>`;
						for(let j=i+1;j<ids.length;j++){
							ids[j] = ids[j] + target2.length - target.length;
						}
						str = str.replace(target, target2);
					}
				});
			}
			if(indicator.globalindicator.value == 'IPv4'){
				let items = indicator.value.split(',');
				items.forEach(item => {
					let reg = new RegExp(item, 'g'), result, ids = [];
					while ( (result = reg.exec(str)) ) {
						ids.push(result.index);
					}
					for(let i=0;i<ids.length;i++){
						console.log(str.substr(ids[i], item.length));
						console.log(str.substr(ids[i]+item.length-1, 1));
						if(!(str.substr(ids[i]+item.length, 1)*1 > 0 && str.substr(ids[i]+item.length, 1)*1 < 9) && str.substr(ids[i]+item.length, 1) != '/'){
							let target = "<span style='background:#faeb42;'>" + item + "</span>";
							let target1 = `<Tooltip title="${indicator.globalindicator.value}=${item}">${target}</Tooltip>`;
							for(let j=i+1;j<ids.length;j++){
								if(!(str.substr(ids[j]+item.length, 1)*1 > 0 && str.substr(ids[j]+item.length, 1)*1 < 9) && str.substr(ids[j]+item.length, 1) != '/')
									ids[j] = ids[j] + target1.length - item.length;
							}
							str = str.substring(0, ids[i]-1) + target1 + str.substr(ids[i]+item.length);
						}
					}
				});
			}
			if(indicator.globalindicator.value == 'IPv4 CIDR'){
				let items = indicator.value.split(',');
				items.forEach(item => {
					let reg = new RegExp(item, 'g'), result, ids = [];
					while ( (result = reg.exec(str)) ) {
						ids.push(result.index);
					}
					for(let i=0;i<ids.length;i++){
						let target = "<span style='background:#faeb42;'>" + item + "</span>";
						let target1 = `<Tooltip title="${indicator.globalindicator.value}=${item}">${target}</Tooltip>`;
						for(let j=i+1;j<ids.length;j++){
							ids[j] = ids[j] + target1.length - item.length;
						}
						str = str.substring(0, ids[i]) + target1 + str.substr(ids[i]+item.length);
					}
				});
			}
			if(indicator.globalindicator.value == 'Country'){
				let items = indicator.value.split(',');
				items.forEach(item => {
					let reg = new RegExp(item, 'g'), result, ids = [];
					while ( (result = reg.exec(str)) ) {
						ids.push(result.index);
					}
					for(let i=0;i<ids.length;i++){
						let target = "<span style='background:#faeb42;'>" + item + "</span>";
						let target1 = `<Tooltip title="${indicator.globalindicator.value}=${item}">${target}</Tooltip>`;
						for(let j=i+1;j<ids.length;j++){
							ids[j] = ids[j] + target1.length - item.length;
						}
						str = str.substring(0, ids[i]) + target1 + str.substr(ids[i]+item.length);
					}
				});
			}
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
					let target1 = `<Tooltip title="${indicator.globalindicator.value}=${temp.join(',')}">${target}</Tooltip>`;
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
		words.forEach(word => {
			let reg = new RegExp(word.trim(), "g");
			str = str.replace(reg, `<span style="background:#00e7ff;">${word.trim()}</span>`)
		});
		document.querySelector("#extraction").innerHTML=str;

	},[]);
	return (
		<Container>
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
				<Grid container>
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
							<p>API call</p>
							<div>
								<span>Feed: </span>
								<span>https://www.cyobstract.com/api/v1/feed?UUID={props.feeditem.feed.uniqueid}</span>
							</div>
							<div>
								<span>Report: </span>
								<span>https://www.cyobstract.com/api/v1/report?UUID={props.uniqueid}</span>
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