import React, { useState } from "react";
import { Container, Grid, TextField, Dialog, DialogActions, DialogContent, DialogTitle } from "@material-ui/core";
import { Table, Tbody, Thead, Th, Tr, Td } from "react-super-responsive-table";
import Alert from '@material-ui/lab/Alert';

const AttributeTable = (props) => {
    const [isEdit, setIsEdit] = useState(false);
    const [isEditAlert, setIsEditAlert] = useState(false);
    const [attribute, setAttribute] = useState(props.attribute.attribute || '');
    const [value, setValue] = useState(props.attribute.value || '');
    const [words, setWords] = useState(props.attribute.words_matched || '');
    const [enabled, setEnabled] = useState(props.attribute.enabled || '');


    return (
        <Tr>
            <Td>{props.attribute.attribute}</Td>
            <Td>{props.attribute.value}</Td>
            <Td>{props.attribute.words_matched}</Td>
            <Td><button className="button is-success" onClick={()=>setIsEdit(true)}>Edit</button>
                <a className="button is-text mx-2" onClick={()=>props.changeStatus(props.index)}>{props.attribute.enabled}</a>
                <Dialog
                    open={isEdit}
                    onClose={()=>setIsEdit(false)}
                    aria-labelledby="alert-dialog-title"
                    aria-describedby="alert-dialog-description"
                >
                    <DialogTitle id="alert-dialog-title">Create new API key</DialogTitle>
                    <DialogContent>
                        {isEditAlert && <Alert severity="error" onClose={()=>setIsEditAlert(false)}>Please input exactly!!!</Alert>}
                        <div className="semisection">
                            <TextField id="outlined-basic1" size="small" value={attribute} placeholder="Observable Type" variant="outlined" onChange={(e)=>setAttribute(e.target.value)} />
                        </div>
                        <div className="semisection">
                            <TextField id="outlined-basic2" size="small" value={value} placeholder="Observable Value" variant="outlined" onChange={(e)=>setValue(e.target.value)} />
                        </div>
                        <div className="semisection">
                            <TextField id="outlined-basic3" size="small" value={words} placeholder="Words to match on" variant="outlined" onChange={(e)=>setWords(e.target.value)} />
                        </div>
                        <div className="semisection">
                            <TextField
                                id="outlined-select-currency-native"
                                select
                                fullWidth
                                size="small"
                                value={enabled}
                                onChange={(e)=>setEnabled(e.target.value)}
                                SelectProps={{
                                    native: true,
                                }}
                                variant="outlined"
                            >
                                <option value="Enable">Enable</option>
                                <option value="Disable">Disable</option>
                            </TextField>
                        </div>
                    </DialogContent>
                    <DialogActions>
                        <button onClick={()=>{props.EditAttribute(props.index, words, value, attribute, enabled); setIsEdit(false)}} className="button is-success" autoFocus>
                            Confirm
                        </button>
                        <button onClick={()=>setIsEdit(false)} className="button is-danger" >
                            Cancel
                        </button>
                    </DialogActions>
                </Dialog>
            </Td>
        </Tr>
    )
}

export default AttributeTable;