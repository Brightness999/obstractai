import React from "react";
import { Tr, Td } from 'react-super-responsive-table';

const IndicatorTable = (props) => {
	return (
		<Tr>
            <Td>{props.indicator.type}</Td>
            <Td>{props.indicator.type_api}</Td>
            <Td>{props.indicator.value}</Td>
            <Td>{props.indicator.value_api}</Td>
            <Td>
                <a onClick={()=>props.Enable(props.index)}>
                    <div className="button is-text">
                        <span>{props.indicator.enabled}</span>
                    </div>
                </a>
            </Td>
        </Tr>
	);
}

export default IndicatorTable;