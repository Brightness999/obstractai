import React from "react";
import { Tr, Td } from 'react-super-responsive-table';

const ListTable = (props) => {
	return (
		<Tr>
            <Td>{`${props.list.globalindicator.type}(${props.list.globalindicator.type_api})`}</Td>
            <Td>{`${props.list.globalindicator.value}(${props.list.globalindicator.value_api})`}</Td>
            <Td>{props.list.value}</Td>
            <Td>
                <div className={props.isAutoDown ? "button is-static" : props.list.enabled=="Enable"?"button is-text":"button is-success"} onClick={()=>props.ListEnable(props.index)}>
                    <span>{props.list.enabled=="Enable"?"Disable":"Enable"}</span>
                </div>
            </Td>
        </Tr>
	);
}

export default ListTable;