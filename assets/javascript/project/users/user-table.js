import React from "react";
import { Tr, Td } from 'react-super-responsive-table';

const UserTable = function (props) {
	let role = ''; let admin = ''; let group = ''; let you='';
	switch(props.role){
		case 0: role = 'Invite Pending'; admin = 'Revoke invite'; break;
		case 1: role = 'Member'; admin = 'Make admin'; group = 'Delete from group'; break; 
		case 2: role = 'Admin'; admin ='Remove admin'; group = 'Delete from group'; break;
	}
	if(props.myId == props.user_id){
		you = '(you)';
		admin = ''; 
		group = '';
	} 
	if(props.group_role == 2){
		return (
			<Tr>
				<Td>{ props.user.email + you }</Td>
				<Td>{ role }</Td>
				<Td>{ Boolean(props.user.last_login) && props.user.last_login.slice(0, 10) }</Td>
				<Td>
						<div className="button is-text">
						<span>
							<a onClick={() => {
								if(props.role == 0)
									props.delete(props.index);
								else props.adminUser(props.role, props.id,);
								}}>
								<span>{admin}</span>
							</a>{ props.role == 0 || props.user_id == props.myId ? '': ' / ' }
							<a onClick={() => props.delete(props.index)}>
								<span>{group}</span>
						</a>
						</span>
					</div>
						
				</Td>
			</Tr>
		);
	}
	else
		return (
			<Tr>
				<Td>{ props.user.email + you}</Td>
				<Td>{ role }</Td>
				<Td>{ Boolean(props.user.last_login) && props.user.last_login.slice(0, 10) }</Td>
			</Tr>
		);
	
}

export default UserTable;
