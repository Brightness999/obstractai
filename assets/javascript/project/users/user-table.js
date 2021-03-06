import React from "react";
import { Tr, Td } from 'react-super-responsive-table';

const UserTable = function (props) {
	let role = ''; let admin = ''; let group = ''; let you='';
	switch(props.role){
		case 0: role = 'Invite Pending'; group = 'Revoke invite'; break;
		case 1: role = 'Member'; admin = 'Make admin'; group = 'Delete from group'; break; 
		case 2: role = 'Admin'; admin ='Remove admin'; group = 'Delete from group'; break;
		case 4: role = 'Request Invite'; admin ='Accept request'; group ='Revoke request'; break;
		default: role = 'Invite Pending'; group ='Revoke invite'; break;
	}
	if(props.myId == props.user_id){
		you = '(you)';
		admin = ''; 
		group = '';
	} 
	if(props.group_role == 2){
		return (
			<Tr>
				<Td>{ props.user ? props.user.email + you : props.email  }</Td>
				<Td>{ role }</Td>
				<Td>{ props.user && Boolean(props.user.last_login) && new Date(props.user.last_login).toLocaleString() }</Td>
				<Td>
						<div className="button is-text">
						<span>
							<a onClick={() => {
								props.adminUser(props.role, props.id,);
							}}>
								<span>{admin}</span>
							</a>{ props.role == 0 || props.user_id == props.myId || !Boolean(props.role) ? '': ' / ' }
							{Boolean(props.user) ? <a onClick={() => props.delete(props.index)}>
								<span>{group}</span>
							</a>:
							<a onClick={() => props.emaildelete(props.index)}>
								<span>{group}</span>
							</a>}
						</span>
					</div>
						
				</Td>
			</Tr>
		);
	}
	
}

export default UserTable;
