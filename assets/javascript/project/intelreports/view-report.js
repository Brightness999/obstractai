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
							str = str.replace(target, `<Tooltip title="${indicator.globalindicator.value}=${url}" arrow>${target1}</Tooltip>`)
						}
					}
				});
			}
			if(indicator.globalindicator.value == 'CVE'){
				console.log(str.substring(6100,6431))
				console.log(str.substring(6450,6600))
				let items = indicator.value.split(',');
				items.forEach(item => {
					console.log(item)
					let reg = new RegExp(item), result, ids = [];
					let re = /17049/gi
					while ( (result = re.exec(str)) ) {
						ids.push(result.index);
					}
					console.log(ids);
				});
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