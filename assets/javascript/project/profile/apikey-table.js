import React from "react";
import { Tr, Td } from 'react-super-responsive-table';


const APIKeyTable = (props) => {
    console.log(props);
    return (
        <Tr>
            <Td>{props.apikey.value}</Td>
            <Td>{props.apikey.name}</Td>
            <Td>{props.apikey.groupids.split(',').map((groupid)=>{
                let str = "";
                props.intelgroups.forEach(intelgroup => {
                    if(intelgroup.intelgroup.id.toString() == groupid){
                        str+=intelgroup.intelgroup.name+",";
                    }
                });
                return str;
            })}</Td>
            <Td><button className="button is-text" onClick={()=>props.deleteAPIKey(props.index)} >Delete</button></Td>
        </Tr>
    );
}

export default APIKeyTable;