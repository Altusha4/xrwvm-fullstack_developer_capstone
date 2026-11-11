const express = require('express');
const mongoose = require('mongoose');
const Dealers = require('./dealership');
const Reviews = require('./review');
const app = express();
app.use(express.json({limit: '32kb'}));
const Counter = mongoose.model('counter', new mongoose.Schema({_id: String, sequence: Number}));
const route = fn => (req, res, next) => Promise.resolve(fn(req, res)).catch(next);
app.get('/', (req, res) => res.json({service:'Dealership API'}));
app.get('/fetchDealers', route(async (req,res) => res.json(await Dealers.find().lean())));
app.get('/fetchDealers/:state', route(async (req,res) => res.json(await Dealers.find({state:req.params.state}).lean())));
app.get('/fetchDealer/:id', route(async (req,res) => res.json(await Dealers.find({id:Number(req.params.id)}).lean())));
app.get('/fetchReviews', route(async (req,res) => res.json(await Reviews.find().lean())));
app.get('/fetchReviews/dealer/:id', route(async (req,res) => res.json(await Reviews.find({dealership:Number(req.params.id)}).lean())));
app.post('/insert_review', route(async (req,res) => {
  const data = req.body;
  if (!data.review || !Number.isInteger(Number(data.dealership))) return res.status(400).json({error:'Invalid review'});
  if (!await Dealers.exists({id:Number(data.dealership)})) return res.status(404).json({error:'Dealer not found'});
  const count = await Counter.findByIdAndUpdate('review', {$inc:{sequence:1}}, {new:true});
  const review = await Reviews.create({...data, id:count.sequence});
  res.status(201).json(review);
}));
app.use((err,req,res,next) => {console.error(err.message);res.status(err.name==='ValidationError'?400:500).json({error:'Request could not be processed'});});
async function start() {
  await mongoose.connect(process.env.MONGO_URL || 'mongodb://localhost:27017/dealershipsDB');
  const dealers=require('./data/dealerships.json').dealerships;
  const reviews=require('./data/reviews.json').reviews;
  for (const d of dealers) await Dealers.updateOne({id:d.id},{$setOnInsert:d},{upsert:true});
  for (const r of reviews) await Reviews.updateOne({id:r.id},{$setOnInsert:r},{upsert:true});
  const largest=await Reviews.findOne().sort({id:-1});
  await Counter.updateOne({_id:'review'},{$max:{sequence:largest?largest.id:0}},{upsert:true});
  app.listen(3030,'0.0.0.0',()=>console.log('Dealership API listening on 3030'));
}
start().catch(err=>{console.error(err.message);process.exit(1);});
