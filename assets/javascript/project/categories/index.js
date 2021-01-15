import React, { useState, useEffect } from "react";
import { Route, Switch, Link, useHistory } from "react-router-dom";
import { Container, TextField, Grid } from "@material-ui/core";
import { Table, Thead, Tbody, Tr, Th } from 'react-super-responsive-table';

import CategoryTable from "./category-table";
import { getAction } from "../../api";
import { API_ROOT } from "../const";

const Loading = () => {
	return (
		<div className='app-card has-text-centered'>
			<div className="lds-ripple"><div></div><div></div></div>
			<p className="heading has-text-primary">Loading...</p>
		</div>
	);
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
		let action
		if(isEdit){
			params['id'] = props.categorylist[index].id
			action = getAction(API_ROOT, ['categories', 'partial_update']);
			if(name.trim() != ''){
				// props.client.action(window.schema, action, params).then((result)=>{
				// 	props.saveCategory(result);
				// 	setBtnText('Add Category');
				// 	setIsEdit(false);
				// 	setName('');
				// });
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
			action = getAction(API_ROOT, ['categories', 'create']);
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
			if(currentrole.role ==0)
				return (
					<div className='app-card has-text-centered'>
						<div className="lds-ripple"><div></div><div></div></div>
						<p className="subtitle is-3">! You have an invitation to <span className="title is-3 has-text-primary">{currentrole.intelgroup.name}</span> pending. <Link className="muted-link subtitle is-3" to="/intelgroups" >Click here to accept.</Link></p>
					</div>
				)
			if(currentrole.role == 1)
				return(
					<div className='section has-text-centered'>
						<p className="subtitle is-3">! You are now a member of <span className="title is-3 has-text-primary">{currentrole.intelgroup.name}</span>.</p>
					</div>
				)
			if(currentrole.role ==2)
				return <CategoryList client={props.client} categorylist={categorylist} saveCategory={saveCategory} deleteCategory={deleteCategory} />
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
		const action = getAction(API_ROOT, ['categories', 'delete']);
		let params = {id: categorylist[index].id};
		// props.client.action(window.schema, action, params).then((result) => {
		// 	const newCategoryList = categorylist.splice(0, index).concat(categorylist.splice(index+1));
		// 	setCategoryList(newCategoryList);
		// });
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