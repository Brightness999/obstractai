import React from "react";
import { Tr, Td } from 'react-super-responsive-table';

const ListTable = (props) => {
	return (
		<Tr>
            <Td>{`${props.list.indicator.globalindicator.type}(${props.list.indicator.globalindicator.type_api})`}</Td>
            <Td>{`${props.list.indicator.globalindicator.value}(${props.list.indicator.globalindicator.value_api})`}</Td>
            <Td>{props.list.value}</Td>
            <Td>
                <div className={props.isAutoDown ? "button is-static" : "button is-text"} onClick={()=>props.ListEnable(props.index)}>
                    <span>{props.list.enabled}</span>
                </div>
            </Td>
        </Tr>
	);
}

export default ListTable;