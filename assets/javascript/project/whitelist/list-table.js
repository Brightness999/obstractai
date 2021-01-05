import React from "react";
import { Tr, Td } from 'react-super-responsive-table';

const ListTable = (props) => {
	return (
		<Tr>
            <Td>{`${props.list.indicator.types}(${props.list.indicator.type_api})`}</Td>
            <Td>{`${props.list.indicator.value}(${props.list.indicator.value_api})`}</Td>
            <Td>{props.list.value}</Td>
            <Td>
                <a onClick={()=>props.ListEnable(props.index)}>
                    <div className="button is-text">
                        <span>{props.list.enabled}</span>
                    </div>
                </a>
            </Td>
        </Tr>
	);
}

export default ListTable;