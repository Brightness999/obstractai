import React from "react";
import { Tr, Td } from 'react-super-responsive-table';

const IndicatorTable = (props) => {
	return (
        <Tr>
            <Td>{`${props.indicator.type}(${props.indicator.type_api})`}</Td>
            <Td>{`${props.indicator.value}(${props.indicator.value_api})`}</Td>
            <Td>
                <a onClick={()=>props.IndicatorEnable(props.index)}>
                    <div className="button is-text">
                        <span>{props.indicator.enabled}</span>
                    </div>
                </a>
            </Td>
        </Tr>
	);
}

export default IndicatorTable;