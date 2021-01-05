import React, { useState, useEffect } from "react";
import { Route, Switch, Link } from "react-router-dom";
import { Container, TextField, Grid } from "@material-ui/core";
import { Table, Thead, Tbody, Tr, Th } from 'react-super-responsive-table';

import CategoryTable from "./category-table";
import { getAction } from "../../api";
import { API_ROOT } from "../const";
import Styles from "../styles";

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
		let auth = new coreapi.auth.SessionAuthentication({
			csrfCookieName: 'csrftoken',
			csrfHeaderName: 'X-CSRFToken'
		});
		const client = new coreapi.Client({auth: auth});
		let params = {
			name: name
		}
		let action
		if(isEdit){
			params['id'] = props.categorylist[index].id
			action = getAction(API_ROOT, ['categories', 'partial_update']);
		}
		else
			action = getAction(API_ROOT, ['categories', 'create']);
		if(name.trim() != ''){
			client.action(window.schema, action, params).then((result)=>{
				props.saveCategory(result);
				setBtnText('Add Category');
				setIsEdit(false);
				setName('');
			});
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
							<TextField id="outlined-basic" value={name} label="Category Name" variant="outlined" onChange={(event)=>setName(event.target.value)} />
						</Grid>
						<Grid item xs={2}>
							<button className="button is-outlined" style={btntext == 'Add Category'? Styles.CategoryAddButton : Styles.CategorySaveButton} onClick={changeCategory}>
								<span>{btntext}</span>
							</button>
						</Grid>
						<Grid item xs={2}>
							{btntext == 'Save' && <button className="button is-outlined" style={{padding:27+'px'}} onClick={()=>{setBtnText('Add Category'); setIsEdit(false); setName('');}}><span>Cancel</span></button>}
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

const Categories = () => {
	let auth = new coreapi.auth.SessionAuthentication({
		csrfCookieName: 'csrftoken',
		csrfHeaderName: 'X-CSRFToken'
	});
	const client = new coreapi.Client({auth: auth});
	const [isLoading, setIsLoading] = useState(true);
	const [categorylist, setCategoryList] = useState([]);

	useEffect(()=>{
		const action = getAction(API_ROOT, ['categories', 'list']);
		client.action(window.schema, action).then((result)=>{
			setCategoryList(result.results);
			setIsLoading(false);
		});
	},[]);

	const CategoryListView = () => {
		if(isLoading)
			return <Loading/>;
		else{
			return <CategoryList categorylist={categorylist} saveCategory={saveCategory} deleteCategory={deleteCategory} />
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
		client.action(window.schema, action, params).then((result) => {
			const newCategoryList = categorylist.splice(0, index).concat(categorylist.splice(index+1));
			setCategoryList(newCategoryList);
		});
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