import React, { useState, useEffect } from "react";
import { Route, Switch, Link, useHistory } from "react-router-dom";
import { Container, TextField, Grid } from "@material-ui/core";
import { Table, Thead, Tbody, Tr, Th } from 'react-super-responsive-table';

import CategoryTable from "./category-table";

const Loading = () => {
	return (
		<div className='app-card has-text-centered'>
			<div className="lds-ripple"><div></div><div></div></div>
			<p className="heading has-text-primary">Loading...</p>
		</div>
	);
}

const Plan = (props) => {
	const [isAlert, setIsAlert] = useState(false);

	const ManagePlan = () => {
		if(props.currentrole.role == 2) location.href=`/subscriptions/intelgroup/${props.currentgroup}`;
		else setIsAlert(true);
	}

	return <div className="my-6">
			<h1 className="title is-size-3 has-text-centered py-6">You must upgrade a plan to perform that action. <a className="tag title is-3" onClick={ManagePlan}>Click here to manage your plan</a></h1>
			{isAlert&& <Grid container direction="row" justify="center" alignItems="center">
				<Grid item xs={6}>
					<Alert className="has-text-centered title is-size-4" severity="error" onClose={()=>setIsAlert(false)}>! Please contact the feed group administrator to manage intel group plan payment to reinstate access.</Alert>
				</Grid>
			</Grid>}
		</div>
}

const CategoryList = (props) => {
	const [name, setName] = useState('');
	const [btntext,setBtnText] = useState('Add Category');
	const [isEdit, setIsEdit] = useState(false);
	const [index, setIndex] = useState('');

	const changeCategory = () => {
		let params = {
			name: name
		}
		if(isEdit){
			params['id'] = props.categorylist[index].id
			if(name.trim() != ''){
				fetch('/api/categories',{
					method: 'put',
					headers: {
						'Content-Type': 'application/json',
						'X-CSRFToken': props.client.transports[0].auth.csrfToken
					},
					credentials: 'same-origin',
					body: JSON.stringify(params)
				}).then(res=>{return res.json()})
				.then(res=>{
					props.saveCategory(res);
					setBtnText('Add Category');
					setIsEdit(false);
					setName('');
				})
			}
		}
		else
		{
			if(name.trim() != ''){
				fetch('/api/categories',{
					method: 'post',
					headers: {
						'Content-Type': 'application/json',
						'X-CSRFToken': props.client.transports[0].auth.csrfToken
					},
					credentials: 'same-origin',
					body: JSON.stringify(params)
				}).then(res=>{return res.json()})
				.then(res=>{
					props.saveCategory(res);
					setBtnText('Add Category');
					setIsEdit(false);
					setName('');
				})
			}
		}
	}

	const editCategory = (index) => {
		setBtnText('Save');
		setName(props.categorylist[index].name);
		setIsEdit(true);
		setIndex(index);
	}

	return (
		<Container>
			<section className="section app-card">
				<h1 className="title is-3">All Categories</h1>
				<div className="section">
					<Grid container>
						<Grid item xs={4}>
							<TextField id="outlined-basic1" value={name} label="Category Name" variant="outlined" onChange={(event)=>setName(event.target.value)} />
						</Grid>
						<Grid item xs={2}>
							{btntext == 'Add Category' && <button className="button is-link is-large" onClick={changeCategory}><span>{btntext}</span></button>}
							{btntext == 'Save' && <button className="button is-success is-large" onClick={changeCategory}><span>{btntext}</span></button>}
						</Grid>
						<Grid item xs={2}>
							{btntext == 'Save' && <button className="button is-outlined is-large" onClick={()=>{setBtnText('Add Category'); setIsEdit(false); setName('');}}><span>Cancel</span></button>}
						</Grid>
					</Grid>
				</div>
				<Table className="table is-striped is-fullwidth has-vcentered-cells">
					<Thead>
						<Tr>
							<Th>ID</Th>
							<Th>Category Name</Th>
							<Th>Action</Th>
						</Tr>
					</Thead>
					<Tbody>
						{
							props.categorylist.map((category, index) => {
								return <CategoryTable index={index} key={category.id} category={category} 
									deleteCategory={(index) => props.deleteCategory(index)} editCategory={(index) => editCategory(index)} />;
							})
						}
					</Tbody>
				</Table>
			</section>
		</Container>
	);

}

const Categories = (props) => {
	const [isLoading, setIsLoading] = useState(true);
	const [categorylist, setCategoryList] = useState([]);
	const [currentrole, setCurrentRole] = useState({});
	const history = useHistory();

	useEffect(()=>{
		if(props.currentgroup == '') history.push('/');
		else{
			let params = {currentgroup:props.currentgroup};
			fetch('/api/categories', {
				method: 'post',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': props.client.transports[0].auth.csrfToken
				},
				credentials: 'same-origin',
				body: JSON.stringify(params)
			}).then(res=>{return res.json()})
			.then(res=>{
				setCategoryList(res.categorylist);
				setCurrentRole(res.currentrole);
				setIsLoading(false);
			})
		}
	},[props.currentgroup]);

	const CategoryListView = () => {
		if(isLoading)
			return <Loading/>;
		else{
			if(props.currentrole.role ==0)
				return (
					<div className='app-card has-text-centered'>
						<div className="lds-ripple"><div></div><div></div></div>
						<p className="subtitle is-3">! You have an invitation to <span className="title is-3 has-text-primary">{props.currentrole.intelgroup.name}</span> pending. <Link className="muted-link subtitle is-3" to="/intelgroups" >Click here to accept.</Link></p>
					</div>
				)
			if(props.currentrole.role == 1)
				return(
					<div className='section has-text-centered'>
						<p className="subtitle is-3">! You are now a member of <span className="title is-3 has-text-primary">{props.currentrole.intelgroup.name}</span>.</p>
					</div>
				)
			if(props.currentrole.role ==2){
				if(props.isPlan)
					return <CategoryList client={props.client} categorylist={categorylist} saveCategory={saveCategory} deleteCategory={deleteCategory} />
				else return <Plan currentgroup={props.currentgroup} currentrole={props.currentrole} />
			}
		}
	}

	const saveCategory = (data) => {
		let flag = false;
		const newCategoryList = [];
		for (let category of categorylist) {
			if (category.id === data.id) {
				newCategoryList.push(data);
				flag = true;
			} else {
				newCategoryList.push(category);
			}
		}
		if (!flag) {
			newCategoryList.push(data);
		}
		setCategoryList(newCategoryList);
	}

	const deleteCategory = (index) => {
		let params = {id: categorylist[index].id};
		fetch('/api/categories',{
			method: 'delete',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': props.client.transports[0].auth.csrfToken
			},
			credentials: 'same-origin',
			body: JSON.stringify(params)
		}).then(res=>{return res.json()})
		.then(res=>{
			const newCategoryList = categorylist.splice(0, index).concat(categorylist.splice(index+1));
			setCategoryList(newCategoryList);
		})
	}

	return (
		<Switch>
			<Route path="/categories" >
				{CategoryListView()}			
			</Route>
		</Switch>
	);
}

export default Categories