import React from "react";
import { Tr, Td } from 'react-super-responsive-table';
import Styles from "../styles";

const CategoryTable = (props) => {
	return (
		<Tr>
			<Td>{props.category? props.category.id: ''}</Td>
			<Td>{props.category? props.category.name: ''}</Td>
			<Td>
				<button className="button is-outlined" style={Styles.CategoryEditButtond} onClick={() => props.editCategory(props.index)}>
					<span>Edit</span>
				</button>
				<a style={{'marginLeft': '1em'}} onClick={() => props.deleteCategory(props.index)}>
					<div className="button is-text">
						<span>Delete</span>
					</div>
				</a>
			</Td>
		</Tr>
	);
}

export default CategoryTable;